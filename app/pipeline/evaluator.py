from typing import List

from app.pipeline.run_pipeline import run_pipeline
from app.schemas.entity import Entity
from app.schemas.evaluation import CaseResult, EvalCase, EvalResult, ExpectedEntity


def _match(detected: Entity, expected: ExpectedEntity) -> bool:
    """Une entité est correcte si le type ET la valeur correspondent."""
    return (
        detected.type == expected.type
        and detected.value.strip() == expected.value.strip()
    )


def _compute_metrics(
    detected: List[Entity],
    expected: List[ExpectedEntity],
) -> tuple[int, int, int, float, float, float]:
    """Calcule TP, FP, FN, précision, rappel et F1."""
    tp = sum(1 for e in expected if any(_match(d, e) for d in detected))
    fp = sum(1 for d in detected if not any(_match(d, e) for e in expected))
    fn = len(expected) - tp

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return tp, fp, fn, round(precision, 4), round(recall, 4), round(f1, 4)


def evaluate_dataset(cases: List[EvalCase]) -> EvalResult:
    """Évalue le pipeline sur un jeu de cas de test."""
    results: List[CaseResult] = []

    total_tp = total_fp = total_fn = 0

    for case in cases:
        response = run_pipeline(case.text)

        tp, fp, fn, precision, recall, f1 = _compute_metrics(
            response.entities, case.expected_entities
        )

        total_tp += tp
        total_fp += fp
        total_fn += fn

        results.append(
            CaseResult(
                id=case.id,
                text=case.text,
                decision=response.decision,
                risk_score=response.risk_score,
                expected_entities=case.expected_entities,
                detected_entities=response.entities,
                true_positives=tp,
                false_positives=fp,
                false_negatives=fn,
                precision=precision,
                recall=recall,
                f1=f1,
            )
        )

    global_precision = (
        total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    )
    global_recall = (
        total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    )
    global_f1 = (
        2 * global_precision * global_recall / (global_precision + global_recall)
        if (global_precision + global_recall) > 0
        else 0.0
    )

    return EvalResult(
        total_cases=len(cases),
        global_precision=round(global_precision, 4),
        global_recall=round(global_recall, 4),
        global_f1=round(global_f1, 4),
        cases=results,
    )
