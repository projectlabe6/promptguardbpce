from unittest.mock import patch

from app.pipeline.masking_engine import apply_masking
from app.schemas.entity import Entity

MOCK_PLACEHOLDERS = {"EMAIL": "[EMAIL]", "IBAN": "[IBAN]", "DEFAULT": "[REDACTED]"}
MOCK_BLOCK_MSG = "[BLOCKED]"


def _make(type: str, value: str, start: int, end: int) -> Entity:
    return Entity(
        type=type, value=value, start=start, end=end, confidence=0.99, source="rules"
    )


@patch("app.pipeline.masking_engine.get_placeholders", return_value=MOCK_PLACEHOLDERS)
@patch("app.pipeline.masking_engine.get_block_message", return_value=MOCK_BLOCK_MSG)
def test_allow_returns_text_unchanged(_, __):
    text = "Bonjour Jean"
    assert apply_masking(text, [], "ALLOW") == text


@patch("app.pipeline.masking_engine.get_placeholders", return_value=MOCK_PLACEHOLDERS)
@patch("app.pipeline.masking_engine.get_block_message", return_value=MOCK_BLOCK_MSG)
def test_block_returns_block_message(_, __):
    assert apply_masking("texte sensible", [], "BLOCK") == MOCK_BLOCK_MSG


@patch("app.pipeline.masking_engine.get_placeholders", return_value=MOCK_PLACEHOLDERS)
@patch("app.pipeline.masking_engine.get_block_message", return_value=MOCK_BLOCK_MSG)
def test_mask_replaces_email(_, __):
    text = "Contact: jean@example.com"
    entity = _make("EMAIL", "jean@example.com", 9, 25)
    result = apply_masking(text, [entity], "MASK")
    assert result == "Contact: [EMAIL]"
    assert "jean@example.com" not in result


@patch("app.pipeline.masking_engine.get_placeholders", return_value=MOCK_PLACEHOLDERS)
@patch("app.pipeline.masking_engine.get_block_message", return_value=MOCK_BLOCK_MSG)
def test_mask_multiple_entities(_, __):
    text = "Email: a@b.com, IBAN: FR7612345"
    entities = [
        _make("EMAIL", "a@b.com", 7, 14),
        _make("IBAN", "FR7612345", 22, 31),
    ]
    result = apply_masking(text, entities, "MASK")
    assert "[EMAIL]" in result
    assert "[IBAN]" in result


@patch("app.pipeline.masking_engine.get_placeholders", return_value=MOCK_PLACEHOLDERS)
@patch("app.pipeline.masking_engine.get_block_message", return_value=MOCK_BLOCK_MSG)
def test_unknown_type_uses_default(_, __):
    text = "valeur inconnue: SECRET123"
    entity = _make("UNKNOWN_TYPE", "SECRET123", 17, 26)
    result = apply_masking(text, [entity], "MASK")
    assert "[REDACTED]" in result
