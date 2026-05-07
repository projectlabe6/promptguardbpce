import time

from app.pipeline.decision_engine import compute_decision
from app.pipeline.entity_fusion import fuse_entities
from app.pipeline.masking_engine import apply_masking
from app.pipeline.ner_medical import detect_entities_medical
from app.pipeline.ner_pii import detect_entities_pii
from app.pipeline.rules_engine import detect_entities
from app.schemas.sanitize import SanitizeResponse


def run_pipeline(text: str) -> SanitizeResponse:
    t_start = time.perf_counter()

    entities_rules = detect_entities(text)
    entities_pii = detect_entities_pii(text)
    entities_medical = detect_entities_medical(text)

    all_entities = fuse_entities(entities_rules, entities_pii, entities_medical)

    decision, risk_score = compute_decision(all_entities)
    sanitized_text = apply_masking(text, all_entities, decision)

    processing_time_ms = round((time.perf_counter() - t_start) * 1000)

    return SanitizeResponse(
        decision=decision,
        risk_score=risk_score,
        sanitized_text=sanitized_text,
        entities=all_entities,
        metadata={
            "entity_count": len(all_entities),
            "processing_time_ms": processing_time_ms,
        },
    )
