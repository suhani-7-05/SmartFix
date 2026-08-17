"""
SmartFix RAG Service — Exercise 3 & 4

FastAPI service for technical manual retrieval, text chunking, embeddings, vector similarity search,
and RAG context construction.
"""

import logging
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add paths for imports
RAG_DIR = Path(__file__).resolve().parent
KB_DIR = RAG_DIR.parent / "knowledge-base"
sys.path.insert(0, str(RAG_DIR))
sys.path.insert(0, str(KB_DIR))

from rag_engine import execute_rag_pipeline, vector_store
from chunker import chunk_text
from config import ALLOWED_EXTENSIONS, CHUNK_OVERLAP, CHUNK_SIZE, DOCUMENTS_DIR, OLLAMA_EMBED_MODEL
import db
from embeddings import EmbeddingError, embed_text
from extractors import extract_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("smartfix.rag-service")

app = FastAPI(
    title="SmartFix RAG Service",
    description="Exercise 3 & 4 — Vector Similarity Search & RAG Context Retrieval",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()


class RAGRetrieveRequest(BaseModel):
    query: str = Field(..., description="Technical question or query")
    top_k: int = Field(default=3, description="Top-K vector matches to retrieve")


@app.get("/health")
async def health_check() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "smartfix-rag-service",
        "embed_model": OLLAMA_EMBED_MODEL,
        "chroma_vectors": vector_store.count(),
    }


@app.get("/stats")
@app.get("/rag/stats")
async def get_stats() -> dict[str, Any]:
    sqlite_stats = db.get_stats()
    chroma_stats = vector_store.stats()
    return {
        "documents": sqlite_stats["document_count"],
        "chunks": sqlite_stats["chunk_count"],
        "embedded_chunks": sqlite_stats["embedded_chunk_count"],
        "vector_store": chroma_stats,
    }


@app.post("/retrieve")
@app.post("/rag/retrieve")
async def retrieve_rag_context(body: RAGRetrieveRequest) -> dict[str, Any]:
    """
    RAG Retrieval Endpoint:
    Question -> Query Embedding -> Vector Similarity -> Top-K Chunks -> Constructed Context
    """
    query_text = body.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query text cannot be empty.")

    try:
        rag_result = await execute_rag_pipeline(query=query_text, top_k=body.top_k)
        return rag_result
    except Exception as exc:
        logger.error("RAG retrieval failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"RAG retrieval failed: {exc}") from exc


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)) -> dict[str, Any]:
    filename = file.filename or "unnamed_document"
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    saved_path = DOCUMENTS_DIR / f"{filename}"

    try:
        content = await file.read()
        saved_path.write_bytes(content)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {exc}") from exc

    doc_record = db.create_document(filename=filename, file_type=ext, file_path=str(saved_path))
    doc_id = doc_record["id"]

    try:
        extracted = extract_text(saved_path, ext)
        chunks = chunk_text(extracted, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)

        for chunk in chunks:
            vector, model_name, dims = await embed_text(chunk.text)
            vector_id = f"vec_{doc_id}_{chunk.chunk_index}"
            vector_store.add_chunk(
                vector_id=vector_id,
                embedding=vector,
                text=chunk.text,
                metadata={"document_id": doc_id, "chunk_index": chunk.chunk_index, "filename": filename},
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

        updated_doc = db.update_document(
            doc_id,
            status="processed",
            extracted_text_length=len(extracted),
            chunk_count=len(chunks),
        )
        return updated_doc
    except Exception as exc:
        db.update_document(doc_id, status="error", error_message=str(exc))
        raise HTTPException(status_code=500, detail=f"Processing document failed: {exc}") from exc


@app.get("/documents")
async def list_documents() -> list[dict[str, Any]]:
    return db.list_documents()


@app.get("/documents/{document_id}/chunks")
async def get_document_chunks(document_id: str) -> list[dict[str, Any]]:
    return db.list_chunks(document_id)


@app.get("/vectors/{vector_id}")
async def get_vector(vector_id: str) -> dict[str, Any]:
    info = vector_store.get_vector(vector_id)
    if not info:
        raise HTTPException(status_code=404, detail="Vector not found.")
    return info
