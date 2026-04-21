from __future__ import annotations

import os
from typing import List, Optional

from transformers import Pipeline, pipeline

from app.schemas.entity import Entity

_CONTAINER_MODEL_DIR = "/app/models/camembert-ner"
_LOCAL_MODEL_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "models", "camembert-ner")
)

MODEL_PATH = (
    _CONTAINER_MODEL_DIR if os.path.isdir(_CONTAINER_MODEL_DIR) else _LOCAL_MODEL_DIR
)

# Mapping labels HuggingFace → types internes
LABEL_MAP = {
    "PER": "PII_PERSON",
    "ORG": "PII_ORGANISATION",
    "LOC": "PII_LOCATION",
    "MISC": "PII_MISC",
}

_pii_pipeline: Optional[Pipeline] = None


def _load_pii_pipeline() -> Pipeline:
    """Charge le pipeline NER en lazy loading."""
    global _pii_pipeline
    if _pii_pipeline is None:
        print(f"[NER-PII] Chargement du modèle depuis : {MODEL_PATH}")
        _pii_pipeline = pipeline(
            "token-classification",
            model=MODEL_PATH,
            aggregation_strategy="simple",
        )
    return _pii_pipeline


def detect_entities_pii(text: str) -> List[Entity]:
    """Détecte les entités PII (personne, organisation, lieu) via CamemBERT-NER."""
    if not text or not text.strip():
        return []

    ner = _load_pii_pipeline()
    raw = ner(text)

    entities: List[Entity] = []
    for ent in raw:
        label = ent.get("entity_group", "")
        ent_type = LABEL_MAP.get(label, f"PII_{label}")

        entities.append(
            Entity(
                type=ent_type,
                value=ent["word"],
                start=int(ent["start"]),
                end=int(ent["end"]),
                confidence=round(float(ent["score"]), 4),
                source="ml",
            )
        )

    return entities
