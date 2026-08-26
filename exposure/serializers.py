from django.db import transaction
from rest_framework import serializers

from devices.models import Device
from exposure.models import (
    ExposureProfile,
    Worker,
)
from exposure.services.inhalation import (
    UnsupportedInhalationMethodologyError,
    resolve_inhalation_methodology,
    sync_worker_exposure_inhalation_rate,
)
from exposure.services.validation import (
    ExposureValidationError,
    validate_exposure_data,
)


class WorkerSerializer(
    serializers.ModelSerializer
):
    name = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=150,
    )

    age = serializers.IntegerField(
        required=True,
        min_value=1,
        max_value=120,
    )

    monitoring_device = (
        serializers.PrimaryKeyRelatedField(
            queryset=Device.objects.filter(
                is_active=True
            ),
            required=False,
            allow_null=True,
        )
    )

    monitoring_device_code = (
        serializers.CharField(
            source="monitoring_device.device_code",
            read_only=True,
            allow_null=True,
        )
    )

    monitoring_device_name = (
        serializers.CharField(
            source="monitoring_device.name",
            read_only=True,
            allow_null=True,
        )
    )

    monitoring_device_location = (
        serializers.CharField(
            source="monitoring_device.location",
            read_only=True,
            allow_null=True,
        )
    )

    class Meta:
        model = Worker

        fields = [
            "id",
            "code",
            "name",
            "age",
            "is_active",
            "monitoring_device",
            "monitoring_device_code",
            "monitoring_device_name",
            "monitoring_device_location",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "monitoring_device_code",
            "monitoring_device_name",
            "monitoring_device_location",
            "created_at",
            "updated_at",
        ]

    def validate_name(
        self,
        value,
    ):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Name cannot be blank."
            )

        return value

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        previous_age = (
            instance.age
        )

        worker = super().update(
            instance,
            validated_data,
        )

        age_changed = (
            "age" in validated_data
            and worker.age != previous_age
        )

        if age_changed:
            try:
                sync_worker_exposure_inhalation_rate(
                    worker
                )

            except (
                UnsupportedInhalationMethodologyError
            ) as exc:
                raise serializers.ValidationError(
                    {
                        "age": str(exc),
                    }
                ) from exc

        return worker


class ExposureProfileSerializer(
    serializers.ModelSerializer
):
    worker_code = serializers.CharField(
        source="worker.code",
        read_only=True,
    )

    worker_name = serializers.CharField(
        source="worker.name",
        read_only=True,
        allow_null=True,
    )

    inhalation_category = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = ExposureProfile

        fields = [
            "id",
            "worker",
            "worker_code",
            "worker_name",
            "body_weight",
            "exposure_time",
            "exposure_frequency",
            "exposure_duration",
            "inhalation_rate",
            "inhalation_category",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "worker_code",
            "worker_name",
            "inhalation_rate",
            "inhalation_category",
            "created_at",
            "updated_at",
        ]

    @staticmethod
    def _resolve_methodology(
        worker: Worker,
    ):
        if worker.age is None:
            raise serializers.ValidationError(
                {
                    "worker": (
                        "Worker age is required "
                        "before creating or updating "
                        "an exposure profile."
                    )
                }
            )

        try:
            return (
                resolve_inhalation_methodology(
                    worker.age
                )
            )

        except (
            UnsupportedInhalationMethodologyError
        ) as exc:
            raise serializers.ValidationError(
                {
                    "worker": str(exc),
                }
            ) from exc

    def get_inhalation_category(
        self,
        obj,
    ):
        if obj.worker.age is None:
            return None

        try:
            methodology = (
                resolve_inhalation_methodology(
                    obj.worker.age
                )
            )

        except (
            UnsupportedInhalationMethodologyError
        ):
            return None

        return methodology.category

    def _get_worker(
        self,
        attrs,
    ) -> Worker:
        if self.instance is not None:
            return self.instance.worker

        worker = attrs.get(
            "worker"
        )

        if worker is None:
            raise serializers.ValidationError(
                {
                    "worker": (
                        "Worker is required."
                    )
                }
            )

        return worker

    def validate(
        self,
        attrs,
    ):
        instance = self.instance

        worker = self._get_worker(
            attrs
        )

        methodology = (
            self._resolve_methodology(
                worker
            )
        )

        inhalation_rate = float(
            methodology.inhalation_rate
        )

        values = {
            "body_weight": attrs.get(
                "body_weight",
                getattr(
                    instance,
                    "body_weight",
                    None,
                ),
            ),
            "exposure_time": attrs.get(
                "exposure_time",
                getattr(
                    instance,
                    "exposure_time",
                    None,
                ),
            ),
            "exposure_frequency": attrs.get(
                "exposure_frequency",
                getattr(
                    instance,
                    "exposure_frequency",
                    None,
                ),
            ),
            "exposure_duration": attrs.get(
                "exposure_duration",
                getattr(
                    instance,
                    "exposure_duration",
                    None,
                ),
            ),
            "inhalation_rate": (
                inhalation_rate
            ),
        }

        try:
            validate_exposure_data(
                **values
            )

        except ExposureValidationError as exc:
            raise serializers.ValidationError(
                {
                    "detail": str(exc),
                }
            ) from exc

        return attrs

    @transaction.atomic
    def create(
        self,
        validated_data,
    ):
        worker = (
            validated_data[
                "worker"
            ]
        )

        methodology = (
            self._resolve_methodology(
                worker
            )
        )

        return (
            ExposureProfile.objects.create(
                **validated_data,
                inhalation_rate=float(
                    methodology.inhalation_rate
                ),
            )
        )

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        methodology = (
            self._resolve_methodology(
                instance.worker
            )
        )

        for field, value in (
            validated_data.items()
        ):
            setattr(
                instance,
                field,
                value,
            )

        instance.inhalation_rate = float(
            methodology.inhalation_rate
        )

        instance.save()

        return instance