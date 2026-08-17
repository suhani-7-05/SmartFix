"""
RAG Engine module — Question embedding, Vector similarity search, Top-K retrieval, Context construction.
"""

import logging
import sys
from pathlib import Path
from typing import Any

KB_DIR = Path(__file__).resolve().parents[1] / "knowledge-base"
if str(KB_DIR) not in sys.path:
    sys.path.insert(0, str(KB_DIR))

from embeddings import embed_text
from vector_store import VectorStore
import db

logger = logging.getLogger("smartfix.rag-engine")

vector_store = VectorStore()


async def execute_rag_pipeline(query: str, top_k: int = 3) -> dict[str, Any]:
    """
    Execute full RAG retrieval pipeline:
    Question -> Query Embedding -> Vector Similarity -> Top-K Chunks -> Context Construction
    """
    db.init_db()
    
    # 1. Compute query embedding
    query_vector, model_name, dimensions = await embed_text(query)

    # 2. Vector similarity search in ChromaDB
    raw_matches = vector_store.search_similar(query_vector, top_k=top_k)

    retrieved_chunks = []
    context_blocks = []

    for match in raw_matches:
        meta = match.get("metadata", {})
        doc_filename = meta.get("filename", "unknown_document")

        chunk_info = {
            "vector_id": match["vector_id"],
            "similarity_score": match["similarity_score"],
            "distance": match["distance"],
            "document_filename": doc_filename,
            "document_id": meta.get("document_id"),
            "chunk_index": meta.get("chunk_index"),
            "text": match["text"],
        }
        retrieved_chunks.append(chunk_info)

        context_blocks.append(
            f"--- Source Document: {doc_filename} (Chunk #{meta.get('chunk_index', 0)}, Similarity: {match['similarity_score']}) ---\n"
            f"{match['text']}"
        )

    constructed_context = "\n\n".join(context_blocks) if context_blocks else "No relevant technical documentation chunks found in vector database."

    return {
        "query": query,
        "query_embedding_metadata": {
            "model": model_name,
            "dimensions": dimensions,
            "vector_preview": [float(x) for x in query_vector[:8]],
        },
        "retrieved_chunks": retrieved_chunks,
        "top_k": top_k,
        "retrieved_count": len(retrieved_chunks),
        "constructed_context": constructed_context,
    }
