from __future__ import annotations

import os
from typing import List, Optional

from gliner import GLiNER

from app.schemas.entity import Entity

_CONTAINER_MODEL_DIR = "/app/models/camembert-bio-gliner-v0.1"
_LOCAL_MODEL_DIR = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "models", "camembert-bio-gliner-v0.1"
    )
)

MODEL_PATH = (
    _CONTAINER_MODEL_DIR if os.path.isdir(_CONTAINER_MODEL_DIR) else _LOCAL_MODEL_DIR
)

MEDICAL_LABELS = [
    "Patient",
    "Âge",
    "Maladie",
    "Symptômes",
    "Médicament",
    "Examen",
    "Acte médical",
    "Traitement",
]

_medical_model: Optional[GLiNER] = None


def _load_medical_model() -> GLiNER:
    """Charge le modèle GLiNER médical en lazy loading."""
    global _medical_model
    if _medical_model is None:
        print(f"[NER-MEDICAL] Chargement du modèle depuis : {MODEL_PATH}")
        _medical_model = GLiNER.from_pretrained(MODEL_PATH, local_files_only=True)
    return _medical_model


def detect_entities_medical(text: str) -> List[Entity]:
    """Détecte les entités médicales via GLiNER."""
    if not text or not text.strip():
        return []

    model = _load_medical_model()
    raw = model.predict_entities(text, MEDICAL_LABELS, threshold=0.5, flat_ner=True)

    entities: List[Entity] = []
    for ent in raw:
        span = ent.get("text", "").strip()
        if not span:
            continue
        start = ent.get("start")
        end = ent.get("end")
        if start is None or end is None:
            continue

        label = ent.get("label", "MEDICAL")
        ent_type = f"MED_{label.upper().replace(' ', '_').replace('Â', 'A')}"

        entities.append(
            Entity(
                type=ent_type,
                value=text[start:end],
                start=int(start),
                end=int(end),
                confidence=round(float(ent.get("score", 0.9)), 4),
                source="medical",
            )
        )

    return entities
