from unittest.mock import patch

from app.pipeline.decision_engine import compute_decision
from app.schemas.entity import Entity

MOCK_WEIGHTS = {"EMAIL": 0.25, "IBAN": 0.60, "DEFAULT": 0.20}
MOCK_THRESHOLDS = {"allow": 0.20, "mask": 0.85}


def _make(type: str, confidence: float = 0.99) -> Entity:
    return Entity(
        type=type, value="x", start=0, end=1, confidence=confidence, source="rules"
    )


@patch("app.pipeline.decision_engine.get_weights", return_value=MOCK_WEIGHTS)
@patch("app.pipeline.decision_engine.get_thresholds", return_value=MOCK_THRESHOLDS)
def test_no_entities_returns_allow(_, __):
    decision, score = compute_decision([])
    assert decision == "ALLOW"
    assert score == 0.0


@patch("app.pipeline.decision_engine.get_weights", return_value=MOCK_WEIGHTS)
@patch("app.pipeline.decision_engine.get_thresholds", return_value=MOCK_THRESHOLDS)
def test_low_score_returns_allow(_, __):
    decision, score = compute_decision([_make("EMAIL", confidence=0.01)])
    assert decision == "ALLOW"


@patch("app.pipeline.decision_engine.get_weights", return_value=MOCK_WEIGHTS)
@patch("app.pipeline.decision_engine.get_thresholds", return_value=MOCK_THRESHOLDS)
def test_medium_score_returns_mask(_, __):
    decision, score = compute_decision([_make("EMAIL", confidence=0.99)])
    assert decision == "MASK"


@patch(
    "app.pipeline.decision_engine.get_weights",
    return_value={"IBAN": 1.0, "DEFAULT": 0.20},
)
@patch("app.pipeline.decision_engine.get_thresholds", return_value=MOCK_THRESHOLDS)
def test_high_score_returns_block(_, __):
    entities = [_make("IBAN") for _ in range(5)]
    decision, score = compute_decision(entities)
    assert decision == "BLOCK"
