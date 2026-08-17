"""Persist and inspect vectors in a local ChromaDB collection."""

import logging
from typing import Any

import chromadb

from config import CHROMA_COLLECTION, CHROMA_DIR, EMBEDDING_DIMENSIONS

logger = logging.getLogger("smartfix.knowledge-base.vector_store")


class VectorStore:
    """Thin wrapper around a persistent ChromaDB collection."""

    def __init__(self) -> None:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self._collection = self._open_collection()

    def _create_collection(self):
        return self._client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            metadata={
                "hnsw:space": "cosine",
                "embedding_dimensions": EMBEDDING_DIMENSIONS,
            },
        )

    def _stored_dimensions(self, collection) -> int | None:
        metadata = collection.metadata or {}
        stored_meta = metadata.get("embedding_dimensions")
        if stored_meta is not None:
            return int(stored_meta)

        if collection.count() == 0:
            return None

        sample = collection.get(limit=1, include=["embeddings"])
        embeddings = sample.get("embeddings")
        if embeddings is not None and len(embeddings) > 0 and embeddings[0] is not None:
            return len(embeddings[0])
        return None

    def _open_collection(self):
        try:
            collection = self._client.get_collection(name=CHROMA_COLLECTION)
        except Exception:
            return self._create_collection()

        stored_dims = self._stored_dimensions(collection)
        if stored_dims is not None and stored_dims != EMBEDDING_DIMENSIONS:
            logger.warning(
                "ChromaDB collection '%s' uses %d-dim vectors but expected %d. "
                "Resetting collection — re-ingest documents to rebuild embeddings.",
                CHROMA_COLLECTION,
                stored_dims,
                EMBEDDING_DIMENSIONS,
            )
            self._client.delete_collection(name=CHROMA_COLLECTION)
            return self._create_collection()

        return collection

    def _validate_embedding(self, embedding: list[float]) -> None:
        if len(embedding) != EMBEDDING_DIMENSIONS:
            raise ValueError(
                f"Embedding dimension mismatch: expected {EMBEDDING_DIMENSIONS}, got {len(embedding)}. "
                "Ensure Ollama embed model and EMBEDDING_DIMENSIONS config are aligned, then re-ingest documents."
            )

    def add_chunk(
        self,
        vector_id: str,
        embedding: list[float],
        text: str,
        metadata: dict[str, Any],
    ) -> None:
        self._validate_embedding(embedding)
        self._collection.add(
            ids=[vector_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata],
        )

    def delete_by_document(self, document_id: str) -> None:
        existing = self._collection.get(where={"document_id": document_id})
        if existing["ids"]:
            self._collection.delete(ids=existing["ids"])

    def get_vector(self, vector_id: str) -> dict[str, Any] | None:
        result = self._collection.get(
            ids=[vector_id],
            include=["embeddings", "documents", "metadatas"],
        )
        if not result["ids"]:
            return None

        embedding = result["embeddings"][0]
        preview = [float(x) for x in embedding[:8]] if (embedding is not None and len(embedding) > 0) else []
        return {
            "vector_id": vector_id,
            "text": result["documents"][0],
            "metadata": result["metadatas"][0],
            "dimensions": len(embedding) if embedding is not None else 0,
            "embedding_preview": preview,
        }

    def search_similar(
        self,
        query_embedding: list[float],
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Perform vector similarity search against ChromaDB collection.

        Returns top-K matching chunks with similarity scores and metadata.
        """
        if self.count() == 0:
            return []

        self._validate_embedding(query_embedding)

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.count()),
            include=["documents", "metadatas", "distances"],
        )

        matches = []
        if results and results.get("ids") and results["ids"][0]:
            ids = results["ids"][0]
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]

            for vec_id, doc_text, meta, dist in zip(ids, docs, metas, distances):
                # Cosine distance: similarity score = 1.0 - distance (or max(0, 1.0 - dist))
                sim_score = max(0.0, round(1.0 - float(dist), 4))
                matches.append(
                    {
                        "vector_id": vec_id,
                        "text": doc_text,
                        "metadata": meta,
                        "distance": round(float(dist), 4),
                        "similarity_score": sim_score,
                    }
                )

        # Sort by highest similarity score first
        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matches

    def count(self) -> int:
        return self._collection.count()

    def stats(self) -> dict[str, Any]:
        return {
            "collection": CHROMA_COLLECTION,
            "persist_path": str(CHROMA_DIR),
            "vector_count": self.count(),
            "embedding_dimensions": EMBEDDING_DIMENSIONS,
        }
