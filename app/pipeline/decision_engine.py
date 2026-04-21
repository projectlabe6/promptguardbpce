from typing import List, Tuple

from app.schemas.entity import Entity


def compute_decision(entities: List[Entity]) -> Tuple[str, float]:
    return ("ALLOW", 0.0)
