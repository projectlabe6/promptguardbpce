import json
from datetime import datetime
from pathlib import Path
from typing import List

from app.config import audit_enabled, audit_file_path
from app.schemas.entity import Entity


def log_audit(
    original_text: str,
    entities: List[Entity],
    decision: str,
    risk_score: float,
) -> None:
    """Enregistre une entrée d'audit en JSON ligne par ligne."""
    if not audit_enabled():
        return

    payload = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "decision": decision,
        "risk_score": risk_score,
        "entities": [e.model_dump() for e in entities],
        "length": len(original_text),
    }

    path = Path(audit_file_path())
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
