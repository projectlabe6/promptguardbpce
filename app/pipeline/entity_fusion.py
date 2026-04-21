from typing import List, Tuple

from app.schemas.entity import Entity


def _key(e: Entity) -> Tuple[str, int, int]:
    return (e.type, e.start, e.end)


def fuse_entities(*entity_lists: List[Entity]) -> List[Entity]:
    """Fusionne plusieurs listes d'entités en supprimant les doublons exacts."""
    seen = set()
    out: List[Entity] = []

    for lst in entity_lists:
        for e in lst:
            k = _key(e)
            if k not in seen:
                seen.add(k)
                out.append(e)

    out.sort(key=lambda x: (x.start, x.end))
    return out
