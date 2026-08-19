from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from arkl.models import ARKLResult
from devices.models import Device
from exposure.models import Worker


class RealtimeARKLRequestSerializer(serializers.Serializer):
    worker = serializers.PrimaryKeyRelatedField(
        queryset=Worker.objects.filter(is_active=True),
    )

    device = serializers.PrimaryKeyRelatedField(
        queryset=Device.objects.filter(is_active=True),
    )


class HistoricalARKLRequestSerializer(serializers.Serializer):
    worker = serializers.PrimaryKeyRelatedField(
        queryset=Worker.objects.filter(is_active=True),
    )

    device = serializers.PrimaryKeyRelatedField(
        queryset=Device.objects.filter(is_active=True),
    )

    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()

    def validate(self, attrs):
        if attrs["start_time"] >= attrs["end_time"]:
            raise serializers.ValidationError(
                {"end_time": ("end_time must be later than start_time.")}
            )

        return attrs


class ARKLResultSerializer(serializers.ModelSerializer):
    worker_code = serializers.CharField(
        source="worker.code",
        read_only=True,
    )

    device_code = serializers.SerializerMethodField()

    class Meta:
        model = ARKLResult
        fields = [
            "id",
            "worker",
            "worker_code",
            "reading",
            "device_code",
            "calculation_type",
            "concentration_ppm",
            "concentration_mg_m3",
            "exposure_concentration_mg_m3",
            "body_weight",
            "exposure_time",
            "exposure_frequency",
            "exposure_duration",
            "inhalation_rate",
            "averaging_time",
            "intake",
            "rfc",
            "rq",
            "interpretation",
            "calculation_version",
            "source_simulated",
            "period_start",
            "period_end",
            "reading_count",
            "created_at",
        ]

        read_only_fields = fields

    @extend_schema_field(
        serializers.CharField(
            allow_null=True,
        )
    )
    def get_device_code(
        self,
        obj: ARKLResult,
    ) -> str | None:
        if obj.reading_id is None:
            return None

        return obj.reading.device.device_code
