from django.db import models

from alerts.services.constants import (
    ALERT_RULE_VERSION,
    AlertLevel,
    AlertLifecycleStatus,
    EnvironmentalSeverity,
    RiskStatus,
)
from arkl.models import ARKLResult
from devices.models import Device, H2SReading
from exposure.models import Worker


class Alert(models.Model):
    worker = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name="alerts",
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.PROTECT,
        related_name="alerts",
    )
    reading = models.ForeignKey(
        H2SReading,
        on_delete=models.PROTECT,
        related_name="alerts",
    )
    arkl_result = models.ForeignKey(
        ARKLResult,
        on_delete=models.PROTECT,
        related_name="alerts",
    )

    # Snapshot of Layer 1.
    concentration_ppm = models.DecimalField(
        max_digits=14,
        decimal_places=6,
    )
    environmental_level = models.PositiveSmallIntegerField()
    environmental_status = models.CharField(
        max_length=64,
    )

    # Canonical Phase 5 normalization.
    environmental_severity = models.CharField(
        max_length=16,
        choices=[(item.value, item.value) for item in EnvironmentalSeverity],
    )

    # Snapshot of Layer 3.
    rq = models.DecimalField(
        max_digits=24,
        decimal_places=12,
    )
    risk_interpretation = models.CharField(
        max_length=32,
    )
    calculation_version = models.CharField(
        max_length=32,
    )

    # Phase 5 decision.
    alert_level = models.CharField(
        max_length=16,
        choices=[(item.value, item.value) for item in AlertLevel],
    )
    risk_status = models.CharField(
        max_length=32,
        choices=[(item.value, item.value) for item in RiskStatus],
    )
    status = models.CharField(
        max_length=16,
        choices=[(item.value, item.value) for item in AlertLifecycleStatus],
        default=AlertLifecycleStatus.OPEN,
    )

    recommendation_codes = models.JSONField(
        default=list,
    )

    alert_rule_version = models.CharField(
        max_length=32,
        default=ALERT_RULE_VERSION,
    )

    source_simulated = models.BooleanField(
        default=False,
    )

    acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(
                fields=["worker", "status"],
                name="alert_worker_status_idx",
            ),
            models.Index(
                fields=["device", "status"],
                name="alert_device_status_idx",
            ),
            models.Index(
                fields=["alert_level", "status"],
                name="alert_level_status_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"Alert {self.pk} - {self.alert_level} - {self.status}"
