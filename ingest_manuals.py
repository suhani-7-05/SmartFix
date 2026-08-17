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
    files = [
        uploads_dir / "hydraulic_pump_hp5000_manual.md",
        uploads_dir / "conveyor_belt_cb200_safety.md",
        uploads_dir / "industrial_motor_im750_spec.md",
    ]
    
    for f_path in files:
        if not f_path.exists():
            continue
        filename = f_path.name
        ext = f_path.suffix.lower()
        print(f"Ingesting {filename}...")
        
        extracted = extract_text(f_path, ext)
        chunks = chunk_text(extracted, chunk_size=400, overlap=50)
        
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
