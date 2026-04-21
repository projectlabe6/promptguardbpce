import re
from typing import List

from app.config import get_rule_patterns
from app.schemas.entity import Entity


def detect_entities(text: str) -> List[Entity]:
    """Détecte les entités sensibles via les regex définis dans settings.json."""
    if not text or not text.strip():
        return []

    entities: List[Entity] = []

    for pattern in get_rule_patterns():
        ent_type = pattern["type"]
        compiled = re.compile(pattern["regex"])

        for match in compiled.finditer(text):
            # Confiance fixée à 0.99 : les regex sont déterministes
            entities.append(
                Entity(
                    type=ent_type,
                    value=match.group(0),
                    start=match.start(),
                    end=match.end(),
                    confidence=0.99,
                    source="rules",
                )
            )

    return entities
