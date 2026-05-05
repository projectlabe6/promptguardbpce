from typing import List, Tuple

from app.schemas.entity import Entity

SOURCE_PRIORITY = {"medical": 3, "ml": 2, "rules": 1}


def _key(e: Entity) -> Tuple[str, int, int]:
    return (e.type, e.start, e.end)


def _overlaps(a: Entity, b: Entity) -> bool:
    """Vérifie si deux entités se chevauchent dans le texte."""
    return a.start < b.end and b.start < a.end


def _priority(e: Entity) -> Tuple[float, int]:
    """Score de priorité : confiance d'abord, puis source."""
    return (e.confidence, SOURCE_PRIORITY.get(e.source, 0))


def fuse_entities(*entity_lists: List[Entity]) -> List[Entity]:
    """Fusionne plusieurs listes d'entités, déduplique et résout les chevauchements."""
    seen = set()
    combined: List[Entity] = []

    for lst in entity_lists:
        for e in lst:
            k = _key(e)
            if k not in seen:
                seen.add(k)
                combined.append(e)

    combined.sort(key=lambda x: (x.start, x.end))

    # Résolution des chevauchements — on garde la meilleure entité
    resolved: List[Entity] = []
    for candidate in combined:
        dominated = False
        to_remove = []

        for i, existing in enumerate(resolved):
            if _overlaps(candidate, existing):
                if _priority(candidate) > _priority(existing):
                    to_remove.append(i)
                else:
                    dominated = True
                    break

        for i in reversed(to_remove):
            resolved.pop(i)

        if not dominated:
            resolved.append(candidate)

    resolved.sort(key=lambda x: (x.start, x.end))
    return resolved
