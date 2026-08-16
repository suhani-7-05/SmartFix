"""Extract plain text from supported document formats."""

from pathlib import Path

from pypdf import PdfReader


def extract_text(file_path: Path, file_type: str) -> str:
    """Read a document file and return normalized plain text."""
    if file_type in {".txt", ".md"}:
        return _normalize_text(file_path.read_text(encoding="utf-8"))

    if file_type == ".pdf":
        return _extract_pdf_text(file_path)

    raise ValueError(f"Unsupported file type: {file_type}")


def _normalize_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned.strip()


def _extract_pdf_text(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages.append(page_text.strip())
    return _normalize_text("\n\n".join(pages))
