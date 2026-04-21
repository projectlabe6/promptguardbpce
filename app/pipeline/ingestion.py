import io
from pathlib import Path

import docx
import pdfplumber
from fastapi import UploadFile

from app.schemas.ingestion import IngestedContent


async def ingest_file(file: UploadFile) -> IngestedContent:
    """Extrait le texte d'un fichier PDF, DOCX ou texte brut."""
    content = await file.read()
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        text = _extract_pdf(content)
    elif ext in (".docx", ".doc"):
        text = _extract_docx(content)
    else:
        text = _extract_text(content)

    return IngestedContent(
        text=text,
        metadata={"filename": filename, "extension": ext, "size": len(content)},
    )


def _extract_pdf(content: bytes) -> str:
    """Extrait le texte page par page depuis un PDF."""
    pages = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                pages.append(page_text)
    return "\n".join(pages)


def _extract_docx(content: bytes) -> str:
    """Extrait le texte des paragraphes d'un fichier DOCX."""
    doc = docx.Document(io.BytesIO(content))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def _extract_text(content: bytes) -> str:
    """Décode un fichier texte brut en UTF-8 avec fallback latin-1."""
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1")
