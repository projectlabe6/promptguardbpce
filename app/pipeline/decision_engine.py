import math
from typing import List, Tuple

from app.config import get_thresholds, get_weights
from app.schemas.entity import Entity


def compute_decision(entities: List[Entity]) -> Tuple[str, float]:
    """Calcule le score de risque et retourne la décision ALLOW / MASK / BLOCK."""
    if not entities:
        return ("ALLOW", 0.0)

    weights = get_weights()
    thresholds = get_thresholds()
    default_w = float(weights.get("DEFAULT", 0.20))

    # score brut = somme des (poids × confiance) pour chaque entité
    score_brut = sum(
        float(weights.get(e.type, default_w)) * float(e.confidence) for e in entities
    )

    # normalisation exponentielle pour éviter la croissance linéaire
    score_normalise = 1.0 - math.exp(-score_brut)
    risk_percent = round(score_normalise * 100.0, 2)

    if score_normalise >= float(thresholds.get("mask", 0.85)):
        return ("BLOCK", risk_percent)
    if score_normalise >= float(thresholds.get("allow", 0.20)):
        return ("MASK", risk_percent)
    return ("ALLOW", risk_percent)
