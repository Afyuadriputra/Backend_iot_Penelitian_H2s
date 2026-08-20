from alerts.services.environmental_mapping import (
    normalize_environmental_status,
)
from alerts.services.evaluator import (
    evaluate_alert_with_recommendations,
)
from alerts.services.exceptions import AlertValidationError
from alerts.services.persistence import (
    AlertPersistenceResult,
    persist_alert_evaluation,
)
from arkl.models import ARKLResult


def evaluate_realtime_arkl_alert(
    *,
    arkl_result: ARKLResult,
) -> AlertPersistenceResult:
    if arkl_result.calculation_type != "REALTIME":
        raise AlertValidationError(
            "Only REALTIME ARKLResult can create realtime alerts."
        )

    if arkl_result.reading_id is None:
        raise AlertValidationError("REALTIME ARKLResult must reference an H2SReading.")

    reading = arkl_result.reading

    environmental_severity = normalize_environmental_status(reading.status)

    evaluation = evaluate_alert_with_recommendations(
        environmental_severity=environmental_severity,
        risk_interpretation=arkl_result.interpretation,
    )

    return persist_alert_evaluation(
        reading=reading,
        arkl_result=arkl_result,
        evaluation=evaluation,
    )
