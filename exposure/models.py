from django.core.validators import MinValueValidator
from django.db import models


class Worker(models.Model):
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code


class ExposureProfile(models.Model):
    worker = models.OneToOneField(
        Worker,
        on_delete=models.CASCADE,
        related_name="exposure_profile",
    )

    body_weight = models.FloatField(
        validators=[MinValueValidator(0.01)],
        help_text="Berat badan dalam kilogram.",
    )

    exposure_time = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Waktu pajanan. Satuan final mengikuti metode ARKL.",
    )

    exposure_frequency = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Frekuensi pajanan. Satuan final mengikuti metode ARKL.",
    )

    exposure_duration = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Durasi pajanan. Satuan final mengikuti metode ARKL.",
    )

    inhalation_rate = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Laju inhalasi. Satuan final mengikuti metode ARKL.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Exposure Profile - {self.worker.code}"
