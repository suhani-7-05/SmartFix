"""Re-embed all stored chunks and rebuild the ChromaDB collection."""

import asyncio
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "services" / "knowledge-base"))

from embeddings import embed_text
from vector_store import VectorStore
import db


async def reindex_embeddings() -> None:
    db.init_db()
    vector_store = VectorStore()

    documents = db.list_documents()
    if not documents:
        print("No documents found in knowledge base.")
        return

    total = 0
    for doc in documents:
        if doc.get("status") != "processed":
            continue

        chunks = db.list_chunks(doc["id"])
        filename = doc.get("filename", "unknown")
        print(f"Re-indexing {filename} ({len(chunks)} chunks)...")

        vector_store.delete_by_document(doc["id"])

        for chunk in chunks:
            vector, model_name, dims = await embed_text(chunk["text"])
            vector_id = chunk.get("vector_id") or f"vec_{doc['id']}_{chunk['chunk_index']}"

            vector_store.add_chunk(
                vector_id=vector_id,
                embedding=vector,
                text=chunk["text"],
                metadata={
                    "document_id": doc["id"],
                    "chunk_index": chunk["chunk_index"],
                    "filename": filename,
                },
            )

            db.update_chunk_embedding(
                chunk["id"],
                embedding_model=model_name,
                embedding_dimensions=dims,
                vector_id=vector_id,
            )
            total += 1

    print(f"Re-indexed {total} chunks. ChromaDB vector count: {vector_store.count()}")


if __name__ == "__main__":
    asyncio.run(reindex_embeddings())
