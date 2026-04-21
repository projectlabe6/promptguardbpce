from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import UploadFile

from app.pipeline.ingestion import (
    _extract_docx,
    _extract_pdf,
    _extract_text,
    ingest_file,
)


def _make_upload(filename: str, content: bytes) -> UploadFile:
    file = MagicMock(spec=UploadFile)
    file.filename = filename
    file.read = AsyncMock(return_value=content)
    return file


async def test_ingest_txt_file():
    file = _make_upload("test.txt", b"Bonjour Jean Dupont")
    result = await ingest_file(file)
    assert result.text == "Bonjour Jean Dupont"
    assert result.metadata["extension"] == ".txt"


async def test_ingest_unknown_extension_falls_back_to_text():
    file = _make_upload("test.csv", b"col1,col2\nval1,val2")
    result = await ingest_file(file)
    assert "col1" in result.text


async def test_ingest_empty_filename():
    file = _make_upload("", b"contenu")
    result = await ingest_file(file)
    assert result.text == "contenu"


def test_extract_text_utf8():
    assert _extract_text("Héllo".encode("utf-8")) == "Héllo"


def test_extract_text_latin1_fallback():
    content = "café".encode("latin-1")
    result = _extract_text(content)
    assert isinstance(result, str)


@patch("app.pipeline.ingestion.pdfplumber.open")
def test_extract_pdf_joins_pages(mock_open):
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "Page 1"
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "Page 2"
    mock_open.return_value.__enter__.return_value.pages = [mock_page1, mock_page2]
    result = _extract_pdf(b"fake-pdf")
    assert result == "Page 1\nPage 2"


@patch("app.pipeline.ingestion.pdfplumber.open")
def test_extract_pdf_skips_empty_pages(mock_open):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = None
    mock_open.return_value.__enter__.return_value.pages = [mock_page]
    result = _extract_pdf(b"fake-pdf")
    assert result == ""


@patch("app.pipeline.ingestion.docx.Document")
def test_extract_docx_joins_paragraphs(mock_doc):
    mock_para1 = MagicMock()
    mock_para1.text = "Paragraphe 1"
    mock_para2 = MagicMock()
    mock_para2.text = "Paragraphe 2"
    mock_doc.return_value.paragraphs = [mock_para1, mock_para2]
    result = _extract_docx(b"fake-docx")
    assert result == "Paragraphe 1\nParagraphe 2"


@patch("app.pipeline.ingestion.docx.Document")
def test_extract_docx_skips_empty_paragraphs(mock_doc):
    mock_para = MagicMock()
    mock_para.text = "   "
    mock_doc.return_value.paragraphs = [mock_para]
    result = _extract_docx(b"fake-docx")
    assert result == ""
