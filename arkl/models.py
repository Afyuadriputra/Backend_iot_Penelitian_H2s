from django.db import models

from devices.models import H2SReading
from exposure.models import Worker


class ARKLResult(models.Model):
    class CalculationType(models.TextChoices):
        REALTIME = "REALTIME", "Realtime"
        HISTORICAL = "HISTORICAL", "Historical"

    worker = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name="arkl_results",
    )

    reading = models.ForeignKey(
        H2SReading,
        on_delete=models.PROTECT,
        related_name="arkl_results",
        null=True,
        blank=True,
    )

    calculation_type = models.CharField(
        max_length=20,
        choices=CalculationType.choices,
    )

    concentration_ppm = models.DecimalField(
        max_digits=14,
        decimal_places=6,
    )

    concentration_mg_m3 = models.DecimalField(
        max_digits=14,
        decimal_places=6,
    )

    exposure_concentration_mg_m3 = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        null=True,
        blank=True,
    )

    # Research / exposure snapshot fields.
    body_weight = models.DecimalField(
        max_digits=10,
        decimal_places=4,
    )

    exposure_time = models.DecimalField(
        max_digits=10,
        decimal_places=4,
    )

    exposure_frequency = models.DecimalField(
        max_digits=10,
        decimal_places=4,
    )

    exposure_duration = models.DecimalField(
        max_digits=10,
        decimal_places=4,
    )

    inhalation_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
    )

    # Legacy v1.0 calculation fields.
    averaging_time = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        null=True,
        blank=True,
    )

    intake = models.DecimalField(
        max_digits=24,
        decimal_places=12,
        null=True,
        blank=True,
    )

    rfc = models.DecimalField(
        max_digits=14,
        decimal_places=8,
    )

    rq = models.DecimalField(
        max_digits=24,
        decimal_places=12,
    )

    interpretation = models.CharField(
        max_length=50,
    )

    calculation_version = models.CharField(
        max_length=30,
    )

    source_simulated = models.BooleanField(
        default=False,
    )

    period_start = models.DateTimeField(
        null=True,
        blank=True,
    )

    period_end = models.DateTimeField(
        null=True,
        blank=True,
    )

    reading_count = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.calculation_type} {self.worker.code} RQ={self.rq}"
