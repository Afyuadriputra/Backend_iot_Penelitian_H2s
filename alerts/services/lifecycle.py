from django.db import transaction
from django.utils import timezone

from alerts.models import Alert
from alerts.services.constants import AlertLifecycleStatus
from alerts.services.exceptions import AlertLifecycleError


@transaction.atomic
def acknowledge_alert(
    alert: Alert,
) -> Alert:
    alert = Alert.objects.select_for_update().get(pk=alert.pk)

    if alert.status == AlertLifecycleStatus.RESOLVED:
        raise AlertLifecycleError("Resolved alert cannot be acknowledged.")

    if alert.status == AlertLifecycleStatus.ACKNOWLEDGED:
        return alert

    alert.status = AlertLifecycleStatus.ACKNOWLEDGED
    alert.acknowledged_at = timezone.now()

    alert.save(
        update_fields=[
            "status",
            "acknowledged_at",
            "updated_at",
        ]
    )

    return alert


@transaction.atomic
def resolve_alert(
    alert: Alert,
) -> Alert:
    alert = Alert.objects.select_for_update().get(pk=alert.pk)

    if alert.status == AlertLifecycleStatus.RESOLVED:
        return alert

    now = timezone.now()

    alert.status = AlertLifecycleStatus.RESOLVED
    alert.resolved_at = now

    update_fields = [
        "status",
        "resolved_at",
        "updated_at",
    ]

    alert.save(update_fields=update_fields)

    return alert
