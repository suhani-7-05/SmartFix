"""SQLite persistence for document and chunk metadata."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from config import SQLITE_PATH


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db() -> None:
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                status TEXT NOT NULL,
                extracted_text_length INTEGER,
                chunk_count INTEGER DEFAULT 0,
                error_message TEXT,
                created_at TEXT NOT NULL,
                processed_at TEXT
            );

            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                char_start INTEGER,
                char_end INTEGER,
                embedding_model TEXT,
                embedding_dimensions INTEGER,
                vector_id TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            );

            CREATE INDEX IF NOT EXISTS idx_chunks_document_id
            ON chunks(document_id);
            """
        )


@contextmanager
def get_connection():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def create_document(filename: str, file_type: str, file_path: str) -> dict[str, Any]:
    document_id = str(uuid4())
    now = _utc_now()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO documents (id, filename, file_type, file_path, status, created_at)
            VALUES (?, ?, ?, ?, 'pending', ?)
            """,
            (document_id, filename, file_type, file_path, now),
        )
    return get_document(document_id)


def list_documents() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM documents ORDER BY created_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def get_document(document_id: str) -> dict[str, Any]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE id = ?", (document_id,)
        ).fetchone()
    if row is None:
        raise KeyError(document_id)
    return dict(row)


def update_document(document_id: str, **fields: Any) -> dict[str, Any]:
    if not fields:
        return get_document(document_id)

    columns = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [document_id]
    with get_connection() as conn:
        conn.execute(f"UPDATE documents SET {columns} WHERE id = ?", values)
    return get_document(document_id)


def delete_chunks_for_document(document_id: str) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))


def delete_document(document_id: str) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
        conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))



def create_chunk(
    document_id: str,
    chunk_index: int,
    text: str,
    char_start: int,
    char_end: int,
    embedding_model: str | None = None,
    embedding_dimensions: int | None = None,
    vector_id: str | None = None,
) -> dict[str, Any]:
    chunk_id = str(uuid4())
    now = _utc_now()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO chunks (
                id, document_id, chunk_index, text, char_start, char_end,
                embedding_model, embedding_dimensions, vector_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                chunk_id,
                document_id,
                chunk_index,
                text,
                char_start,
                char_end,
                embedding_model,
                embedding_dimensions,
                vector_id,
                now,
            ),
        )
    return get_chunk(chunk_id)


def list_chunks(document_id: str) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM chunks
            WHERE document_id = ?
            ORDER BY chunk_index ASC
            """,
            (document_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_chunk(chunk_id: str) -> dict[str, Any]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM chunks WHERE id = ?", (chunk_id,)).fetchone()
    if row is None:
        raise KeyError(chunk_id)
    return dict(row)


def get_stats() -> dict[str, Any]:
    with get_connection() as conn:
        doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        chunk_count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        embedded_count = conn.execute(
            "SELECT COUNT(*) FROM chunks WHERE vector_id IS NOT NULL"
        ).fetchone()[0]
    return {
        "document_count": doc_count,
        "chunk_count": chunk_count,
        "embedded_chunk_count": embedded_count,
    }
