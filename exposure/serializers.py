from rest_framework import serializers

from exposure.models import ExposureProfile, Worker
from exposure.services.validation import (
    ExposureValidationError,
    validate_exposure_data,
)


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = [
            "id",
            "code",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class ExposureProfileSerializer(serializers.ModelSerializer):
    worker_code = serializers.CharField(
        source="worker.code",
        read_only=True,
    )

    class Meta:
        model = ExposureProfile
        fields = [
            "id",
            "worker",
            "worker_code",
            "body_weight",
            "exposure_time",
            "exposure_frequency",
            "exposure_duration",
            "inhalation_rate",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "worker_code",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        instance = self.instance

        values = {
            "body_weight": attrs.get(
                "body_weight",
                getattr(instance, "body_weight", None),
            ),
            "exposure_time": attrs.get(
                "exposure_time",
                getattr(instance, "exposure_time", None),
            ),
            "exposure_frequency": attrs.get(
                "exposure_frequency",
                getattr(instance, "exposure_frequency", None),
            ),
            "exposure_duration": attrs.get(
                "exposure_duration",
                getattr(instance, "exposure_duration", None),
            ),
            "inhalation_rate": attrs.get(
                "inhalation_rate",
                getattr(instance, "inhalation_rate", None),
            ),
        }

        try:
            validate_exposure_data(**values)

        except ExposureValidationError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc

        return attrs
