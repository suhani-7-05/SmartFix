"""Generate text embeddings through the local Ollama API."""

import logging

import httpx

from config import OLLAMA_BASE_URL, OLLAMA_EMBED_MODEL, OLLAMA_TIMEOUT_SECONDS

logger = logging.getLogger("smartfix.knowledge-base.embeddings")


class EmbeddingError(Exception):
    """Raised when Ollama embedding generation fails."""


import hashlib
import math


def _generate_fallback_vector(text: str, dimensions: int = 384) -> list[float]:
    """Generate a deterministic 384-dimensional normalized vector for offline/testing mode."""
    vec = []
    text_bytes = text.encode("utf-8")
    for i in range(dimensions):
        h = hashlib.sha256(text_bytes + str(i).encode("utf-8")).digest()
        val = (int.from_bytes(h[:4], "big") / 4294967295.0) * 2.0 - 1.0
        vec.append(val)

    # Normalize vector to unit length
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


async def embed_text(text: str, allow_fallback: bool = True) -> tuple[list[float], str, int]:
    """
    Request an embedding vector from Ollama.

    If Ollama is offline and allow_fallback is True, generates a deterministic
    unit-normalized vector and labels the model as 'nomic-embed-text (offline-fallback)'.
    """
    url = f"{OLLAMA_BASE_URL}/api/embeddings"
    payload = {"model": OLLAMA_EMBED_MODEL, "prompt": text}

    logger.info("Generating embedding with model '%s'", OLLAMA_EMBED_MODEL)

    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT_SECONDS) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 404:
                url_v2 = f"{OLLAMA_BASE_URL}/api/embed"
                payload_v2 = {"model": OLLAMA_EMBED_MODEL, "input": text}
                response = await client.post(url_v2, json=payload_v2)

            response.raise_for_status()
            data = response.json()
            vector = data.get("embedding", [])
            if not vector and "embeddings" in data and len(data["embeddings"]) > 0:
                vector = data["embeddings"][0]

            if vector:
                return vector, OLLAMA_EMBED_MODEL, len(vector)
    except Exception as exc:
        if not allow_fallback:
            if isinstance(exc, httpx.ConnectError):
                raise EmbeddingError(
                    f"Ollama is unavailable at {OLLAMA_BASE_URL}. Start Ollama and run 'ollama pull {OLLAMA_EMBED_MODEL}'."
                ) from exc
            raise EmbeddingError(f"Ollama embedding error: {exc}") from exc

        logger.warning(
            "Ollama embedding API call failed (%s). Using deterministic offline fallback vector.",
            exc,
        )
        fallback_vec = _generate_fallback_vector(text, dimensions=384)
        return fallback_vec, f"{OLLAMA_EMBED_MODEL} (offline-fallback)", len(fallback_vec)

    if allow_fallback:
        fallback_vec = _generate_fallback_vector(text, dimensions=384)
        return fallback_vec, f"{OLLAMA_EMBED_MODEL} (offline-fallback)", len(fallback_vec)

    raise EmbeddingError("Ollama returned an empty embedding vector.")


