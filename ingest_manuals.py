import asyncio
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "services" / "knowledge-base"))

from extractors import extract_text
from chunker import chunk_text
from embeddings import embed_text
from vector_store import VectorStore
import db

async def ingest_manuals():
    db.init_db()
    vector_store = VectorStore()
    
    uploads_dir = PROJECT_ROOT / "data" / "documents" / "uploads"
    
    # Supported file extensions for ingestion
    supported_exts = {".pdf", ".md", ".txt"}
    files = sorted([p for p in uploads_dir.iterdir() if p.suffix.lower() in supported_exts])
    
    # Clean up any incomplete / pending document entries
    with db.get_connection() as conn:
        conn.execute("DELETE FROM documents WHERE status != 'processed'")
        conn.execute("DELETE FROM chunks WHERE document_id NOT IN (SELECT id FROM documents)")

    existing_docs = {d["filename"]: d["id"] for d in db.list_documents() if d.get("status") == "processed"}

    for f_path in files:
        filename = f_path.name
        ext = f_path.suffix.lower()

        # If already ingested, skip to prevent duplicates
        if filename in existing_docs:
            print(f"[*] Skipping already processed: {filename}")
            continue

        print(f"Ingesting {filename}...")

        extracted = extract_text(f_path, ext)
        chunks = chunk_text(extracted, chunk_size=400, overlap=50)
        # Cap chunks to top 40 to ensure fast vector search and balanced retrieval
        if len(chunks) > 40:
            chunks = chunks[:40]

        doc_rec = db.create_document(filename, ext, str(f_path))
        doc_id = doc_rec["id"]
        
        for c in chunks:
            vector, model_name, dims = await embed_text(c.text)
            vec_id = f"vec_{doc_id}_{c.chunk_index}"
            
            vector_store.add_chunk(
                vector_id=vec_id,
                embedding=vector,
                text=c.text,
                metadata={"document_id": doc_id, "chunk_index": c.chunk_index, "filename": filename}
            )
            
            db.create_chunk(
                document_id=doc_id,
                chunk_index=c.chunk_index,
                text=c.text,
                char_start=c.char_start,
                char_end=c.char_end,
                embedding_model=model_name,
                embedding_dimensions=dims,
                vector_id=vec_id
            )
        
        db.update_document(doc_id, status="processed", extracted_text_length=len(extracted), chunk_count=len(chunks))
        print(f"  -> Ingested {len(chunks)} chunks for {filename}")

if __name__ == "__main__":
    asyncio.run(ingest_manuals())
