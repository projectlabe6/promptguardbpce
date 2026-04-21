from typing import List

from app.config import get_block_message, get_placeholders
from app.schemas.entity import Entity


def apply_masking(text: str, entities: List[Entity], decision: str) -> str:
    """Remplace les entités par leurs placeholders selon la décision."""
    if decision == "ALLOW":
        return text
    if decision == "BLOCK":
        return get_block_message()

    placeholders = get_placeholders()

    # remplacement en sens inverse pour ne pas décaler les index
    out = text
    for e in sorted(entities, key=lambda x: x.start, reverse=True):
        placeholder = placeholders.get(
            e.type, placeholders.get("DEFAULT", "[REDACTED]")
        )
        out = out[: e.start] + placeholder + out[e.end :]

    return out
