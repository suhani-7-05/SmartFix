"""Split extracted document text into overlapping chunks."""

from dataclasses import dataclass


@dataclass
class TextChunk:
    chunk_index: int
    text: str
    char_start: int
    char_end: int


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[TextChunk]:
    """
    Split text into fixed-size chunks with overlap.

    Overlap helps preserve context across chunk boundaries for later retrieval.
    """
    if not text.strip():
        return []

    chunks: list[TextChunk] = []
    start = 0
    index = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        piece = text[start:end].strip()
        if piece:
            chunks.append(
                TextChunk(
                    chunk_index=index,
                    text=piece,
                    char_start=start,
                    char_end=end,
                )
            )
            index += 1

        if end >= len(text):
            break

        start = max(end - overlap, start + 1)

    return chunks
