from typing import List

from app.schemas.entity import Entity


def apply_masking(text: str, entities: List[Entity], decision: str) -> str:
    raise NotImplementedError
