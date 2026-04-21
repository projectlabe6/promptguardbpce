from typing import List

from pydantic import BaseModel, Field

from app.schemas.entity import Entity


class ExpectedEntity(BaseModel):
    type: str
    value: str


class EvalCase(BaseModel):
    id: str
    text: str
    expected_entities: List[ExpectedEntity] = Field(default_factory=list)


class CaseResult(BaseModel):
    id: str
    text: str
    decision: str
    risk_score: float
    expected_entities: List[ExpectedEntity]
    detected_entities: List[Entity]
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1: float


class EvalResult(BaseModel):
    total_cases: int
    global_precision: float
    global_recall: float
    global_f1: float
    cases: List[CaseResult]
