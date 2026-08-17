"""Configuration for the SmartFix Knowledge Base service."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("SMARTFIX_DATA_DIR", PROJECT_ROOT / "data"))
DOCUMENTS_DIR = DATA_DIR / "documents" / "uploads"
CHROMA_DIR = DATA_DIR / "chroma"
SQLITE_PATH = DATA_DIR / "knowledge-base.db"

OLLAMA_BASE_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))

# nomic-embed-text produces 768-dimensional vectors; offline fallback must match.
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "768"))

CHUNK_SIZE = int(os.getenv("KB_CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("KB_CHUNK_OVERLAP", "50"))
CHROMA_COLLECTION = os.getenv("KB_CHROMA_COLLECTION", "smartfix_chunks")

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf"}
