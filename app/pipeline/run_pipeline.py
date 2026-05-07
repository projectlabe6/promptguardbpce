import time
from concurrent.futures import ThreadPoolExecutor

from app.pipeline.decision_engine import compute_decision
from app.pipeline.entity_fusion import fuse_entities
from app.pipeline.masking_engine import apply_masking
from app.pipeline.ner_medical import detect_entities_medical
from app.pipeline.ner_pii import detect_entities_pii
from app.pipeline.rules_engine import detect_entities
from app.schemas.sanitize import SanitizeResponse


def run_pipeline(text: str) -> SanitizeResponse:
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=3) as executor:
        fut_rules   = executor.submit(detect_entities, text)
        fut_pii     = executor.submit(detect_entities_pii, text)
        fut_medical = executor.submit(detect_entities_medical, text)

    all_entities = fuse_entities(
        fut_rules.result(), fut_pii.result(), fut_medical.result()
    )

    decision, risk_score = compute_decision(all_entities)
    sanitized_text = apply_masking(text, all_entities, decision)

    execution_time_ms = (time.perf_counter() - start) * 1000

    return SanitizeResponse(
        decision=decision,
        risk_score=risk_score,
        sanitized_text=sanitized_text,
        entities=all_entities,
        metadata={"entity_count": len(all_entities)},
        execution_time_ms=round(execution_time_ms, 1),
    )
