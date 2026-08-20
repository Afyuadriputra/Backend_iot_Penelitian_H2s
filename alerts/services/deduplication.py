from alerts.models import Alert
from alerts.services.constants import (
    ALERT_LEVEL_PRIORITY,
    AlertLevel,
    AlertLifecycleStatus,
)

ACTIVE_ALERT_STATUSES = (
    AlertLifecycleStatus.OPEN,
    AlertLifecycleStatus.ACKNOWLEDGED,
)


def find_latest_active_alert(
    *,
    worker,
    device,
) -> Alert | None:
    return (
        Alert.objects.filter(
            worker=worker,
            device=device,
            status__in=ACTIVE_ALERT_STATUSES,
        )
        .order_by("-created_at", "-id")
        .first()
    )


def find_active_duplicate(
    *,
    worker,
    device,
    alert_level,
) -> Alert | None:
    level = AlertLevel(alert_level)

    return (
        Alert.objects.filter(
            worker=worker,
            device=device,
            alert_level=level,
            status__in=ACTIVE_ALERT_STATUSES,
        )
        .order_by("-created_at", "-id")
        .first()
    )


def is_escalation(
    *,
    existing_alert: Alert,
    new_alert_level,
) -> bool:
    current_level = AlertLevel(existing_alert.alert_level)
    incoming_level = AlertLevel(new_alert_level)

    return ALERT_LEVEL_PRIORITY[incoming_level] > ALERT_LEVEL_PRIORITY[current_level]
