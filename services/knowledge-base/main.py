"""
SmartFix Technical Knowledge Base Service — Exercise 2

FastAPI service for document ingestion, text extraction, chunking,
Ollama embedding generation, SQLite metadata tracking, and ChromaDB vector persistence.
"""

import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure current directory is in sys.path for local imports
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from chunker import chunk_text
from config import (
    ALLOWED_EXTENSIONS,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DOCUMENTS_DIR,
    OLLAMA_EMBED_MODEL,
)
import db
from embeddings import EmbeddingError, embed_text
from extractors import extract_text
from vector_store import VectorStore

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("smartfix.knowledge-base")

# ---------------------------------------------------------------------------
# App & Vector Store Initialization
# ---------------------------------------------------------------------------
app = FastAPI(
    title="SmartFix Knowledge Base Service",
    description="Exercise 2 — Document ingestion, chunking, embeddings, and vector DB",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQLite tables and ChromaDB vector store
db.init_db()
vector_store = VectorStore()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "smartfix-knowledge-base",
        "embed_model": OLLAMA_EMBED_MODEL,
        "chroma_vectors": vector_store.count(),
    }


@app.get("/kb/stats")
@app.get("/stats")
async def get_stats() -> dict[str, Any]:
    """Return Knowledge Base overall statistics."""
    sqlite_stats = db.get_stats()
    chroma_stats = vector_store.stats()
    return {
        "documents": sqlite_stats["document_count"],
        "chunks": sqlite_stats["chunk_count"],
        "embedded_chunks": sqlite_stats["embedded_chunk_count"],
        "vector_store": chroma_stats,
    }


@app.post("/documents/upload")
@app.post("/kb/documents/upload")
async def upload_document(file: UploadFile = File(...)) -> dict[str, Any]:
    """
    Ingest a document file (.txt, .md, .pdf).

    Full pipeline:
    Save -> Extract plain text -> Chunk text -> Compute Ollama embeddings -> Store in ChromaDB & SQLite
    """
    filename = file.filename or "unnamed_document"
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    saved_path = DOCUMENTS_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"

    try:
        content = await file.read()
        saved_path.write_bytes(content)
    except Exception as exc:
        logger.error("Failed to save uploaded file %s: %s", filename, exc)
        raise HTTPException(status_code=500, detail=f"Failed to save file: {exc}") from exc

    doc_record = db.create_document(
        filename=filename,
        file_type=ext,
        file_path=str(saved_path),
    )
    doc_id = doc_record["id"]

    try:
        extracted = extract_text(saved_path, ext)
        if not extracted.strip():
            db.update_document(
                doc_id,
                status="error",
                error_message="Document appears empty or contains no extractable text.",
            )
            raise HTTPException(
                status_code=400,
                detail="Extracted text is empty. Please upload a document with readable text.",
            )

        chunks = chunk_text(extracted, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)

        embedded_count = 0
        for chunk in chunks:
            vector, model_name, dims = await embed_text(chunk.text)
            vector_id = f"vec_{doc_id}_{chunk.chunk_index}"

            vector_store.add_chunk(
                vector_id=vector_id,
                embedding=vector,
                text=chunk.text,
                metadata={
                    "document_id": doc_id,
                    "chunk_index": chunk.chunk_index,
                    "filename": filename,
                },
            )

            db.create_chunk(
                document_id=doc_id,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                char_start=chunk.char_start,
                char_end=chunk.char_end,
                embedding_model=model_name,
                embedding_dimensions=dims,
                vector_id=vector_id,
            )
            embedded_count += 1

        updated_doc = db.update_document(
            doc_id,
            status="processed",
            extracted_text_length=len(extracted),
            chunk_count=len(chunks),
            processed_at=_utc_now(),
        )

        logger.info(
            "Successfully processed '%s' (%d chars, %d chunks embedded)",
            filename,
            len(extracted),
            embedded_count,
        )
        return updated_doc

    except EmbeddingError as exc:
        db.update_document(doc_id, status="error", error_message=str(exc))
        logger.error("Embedding generation failed for document %s: %s", doc_id, exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    except Exception as exc:
        db.update_document(doc_id, status="error", error_message=str(exc))
        logger.error("Processing document %s failed: %s", doc_id, exc)
        raise HTTPException(status_code=500, detail=f"Document processing failed: {exc}") from exc


@app.get("/documents")
@app.get("/kb/documents")
async def list_documents() -> list[dict[str, Any]]:
    """List all ingested documents."""
    return db.list_documents()


@app.get("/documents/{document_id}")
@app.get("/kb/documents/{document_id}")
async def get_document(document_id: str) -> dict[str, Any]:
    """Retrieve document metadata."""
    try:
        return db.get_document(document_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found.")


@app.get("/documents/{document_id}/chunks")
@app.get("/kb/documents/{document_id}/chunks")
async def get_document_chunks(document_id: str) -> list[dict[str, Any]]:
    """Retrieve chunk list for a specific document."""
    try:
        # Verify doc exists
        db.get_document(document_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found.")

    return db.list_chunks(document_id)


@app.get("/chunks/{chunk_id}")
@app.get("/kb/chunks/{chunk_id}")
async def get_chunk(chunk_id: str) -> dict[str, Any]:
    """Retrieve a single chunk details by ID."""
    try:
        return db.get_chunk(chunk_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Chunk not found.")


@app.get("/vectors/{vector_id}")
@app.get("/kb/vectors/{vector_id}")
async def get_vector(vector_id: str) -> dict[str, Any]:
    """Retrieve vector metadata and embedding preview from ChromaDB."""
    info = vector_store.get_vector(vector_id)
    if not info:
        raise HTTPException(status_code=404, detail="Vector not found in vector store.")
    return info


@app.delete("/documents/{document_id}")
@app.delete("/kb/documents/{document_id}")
async def delete_document(document_id: str) -> dict[str, str]:
    """Delete a document, its SQLite chunk metadata, and ChromaDB vector embeddings."""
    try:
        doc = db.get_document(document_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Remove stored document file if exists
    try:
        file_p = Path(doc.get("file_path", ""))
        if file_p.exists():
            file_p.unlink()
    except Exception as exc:
        logger.warning("Could not delete physical file for doc %s: %s", document_id, exc)

    # Delete from ChromaDB
    vector_store.delete_by_document(document_id)

    # Delete from SQLite
    db.delete_document(document_id)

    logger.info("Deleted document %s (%s)", document_id, doc.get("filename"))
    return {"status": "deleted", "id": document_id, "filename": doc.get("filename")}
