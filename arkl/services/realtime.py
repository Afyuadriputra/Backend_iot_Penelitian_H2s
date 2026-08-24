from dataclasses import dataclass

from django.db import transaction

from alerts.services.alert_service import (
    evaluate_realtime_arkl_alert,
)
from alerts.services.exceptions import (
    AlertValidationError,
)
from alerts.services.persistence import (
    AlertPersistenceResult,
)
from arkl.models import ARKLResult
from arkl.services.calculator import (
    ARKLCalculationError,
    calculate_realtime_risk,
)
from devices.models import Device
from exposure.models import Worker


class RealtimeARKLError(ValueError):
    """
    Public application-level error for
    realtime ARKL orchestration.
    """


@dataclass(frozen=True)
class RealtimeARKLExecutionResult:
    arkl_result: ARKLResult
    alert_evaluation: AlertPersistenceResult


@transaction.atomic
def run_realtime_arkl(
    *,
    worker: Worker,
    device: Device,
) -> RealtimeARKLExecutionResult:
    """
    Canonical realtime ARKL workflow.

    1. Validate and calculate ARKL.
    2. Persist ARKLResult.
    3. Evaluate deterministic Alert rules.
    4. Persist Alert lifecycle decision.
    5. Commit both as one application action.
    """
    try:
        arkl_result = (
            calculate_realtime_risk(
                worker=worker,
                device=device,
            )
        )

        alert_evaluation = (
            evaluate_realtime_arkl_alert(
                arkl_result=(
                    arkl_result
                )
            )
        )
    except (
        ARKLCalculationError,
        AlertValidationError,
    ) as exc:
        raise RealtimeARKLError(
            str(exc)
        ) from exc

    return (
        RealtimeARKLExecutionResult(
            arkl_result=arkl_result,
            alert_evaluation=(
                alert_evaluation
            ),
        )
    )