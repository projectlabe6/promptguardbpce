from unittest.mock import patch

from app.pipeline.rules_engine import detect_entities

MOCK_PATTERNS = [
    {"type": "EMAIL", "regex": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"},
    {"type": "PHONE", "regex": r"\b(?:\+33|0)[1-9](?:[\s.-]?\d{2}){4}\b"},
    {"type": "IBAN", "regex": r"\b[A-Z]{2}\d{2}[A-Z0-9]{4,30}\b"},
    {
        "type": "CREDIT_CARD",
        "regex": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b",
    },
]


@patch("app.pipeline.rules_engine.get_rule_patterns", return_value=MOCK_PATTERNS)
def test_detect_email(_):
    entities = detect_entities("Contactez jean@example.com pour info")
    assert len(entities) == 1
    assert entities[0].type == "EMAIL"
    assert entities[0].value == "jean@example.com"
    assert entities[0].source == "rules"
    assert entities[0].confidence == 0.99


@patch("app.pipeline.rules_engine.get_rule_patterns", return_value=MOCK_PATTERNS)
def test_detect_phone(_):
    entities = detect_entities("Appelez le 06 12 34 56 78")
    assert len(entities) == 1
    assert entities[0].type == "PHONE"


@patch("app.pipeline.rules_engine.get_rule_patterns", return_value=MOCK_PATTERNS)
def test_detect_iban(_):
    entities = detect_entities("Mon IBAN est FR7630006000011234567890189")
    assert any(e.type == "IBAN" for e in entities)


@patch("app.pipeline.rules_engine.get_rule_patterns", return_value=MOCK_PATTERNS)
def test_detect_credit_card(_):
    entities = detect_entities("Ma carte est 4111111111111111")
    assert len(entities) == 1
    assert entities[0].type == "CREDIT_CARD"


@patch("app.pipeline.rules_engine.get_rule_patterns", return_value=MOCK_PATTERNS)
def test_empty_text_returns_empty(_):
    assert detect_entities("") == []
    assert detect_entities("   ") == []


@patch("app.pipeline.rules_engine.get_rule_patterns", return_value=MOCK_PATTERNS)
def test_no_entities_returns_empty(_):
    assert detect_entities("Bonjour, comment allez-vous ?") == []
