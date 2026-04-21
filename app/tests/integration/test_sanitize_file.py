from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.ingestion import IngestedContent


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


async def test_sanitize_file_returns_valid_response(client):
    mock = AsyncMock(return_value=IngestedContent(text="jean@example.com", metadata={}))
    with patch("app.api.routes.ingest_file", mock):
        response = await client.post(
            "/sanitize-file",
            files={"file": ("test.txt", b"jean@example.com", "text/plain")},
        )
    assert response.status_code == 200
    data = response.json()
    assert "decision" in data
    assert "risk_score" in data
    assert "sanitized_text" in data


async def test_sanitize_file_clean_text_returns_allow(client):
    mock = AsyncMock(
        return_value=IngestedContent(text="texte sans donnees sensibles", metadata={})
    )
    with patch("app.api.routes.ingest_file", mock):
        response = await client.post(
            "/sanitize-file",
            files={"file": ("test.txt", b"texte sans donnees sensibles", "text/plain")},
        )
    assert response.status_code == 200
    assert response.json()["decision"] == "ALLOW"
