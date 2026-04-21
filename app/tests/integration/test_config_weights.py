from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

MOCK_WEIGHTS = {"EMAIL": 0.25, "PHONE": 0.25, "IBAN": 0.60, "DEFAULT": 0.20}


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@patch("app.api.routes.get_weights", return_value=MOCK_WEIGHTS)
async def test_get_weights_returns_dict(_, client):
    response = await client.get("/config/weights")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "EMAIL" in data


@patch("app.api.routes.get_weights", return_value=MOCK_WEIGHTS)
async def test_get_weights_values_are_floats(_, client):
    response = await client.get("/config/weights")
    data = response.json()
    for value in data.values():
        assert isinstance(value, float)


@patch("app.api.routes.update_weights")
async def test_post_weights_returns_success(mock_update, client):
    response = await client.post(
        "/config/weights",
        json={"weights": {"EMAIL": 0.50}},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Poids mis à jour"
    mock_update.assert_called_once_with({"EMAIL": 0.50})


@patch("app.api.routes.update_weights")
async def test_post_weights_invalid_payload(mock_update, client):
    response = await client.post(
        "/config/weights",
        json={"invalid_key": 123},
    )
    assert response.status_code == 422
