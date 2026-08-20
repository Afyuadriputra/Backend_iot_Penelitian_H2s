from rest_framework import serializers

from alerts.models import Alert
from arkl.models import ARKLResult


class AlertSerializer(serializers.ModelSerializer):
    worker_code = serializers.CharField(
        source="worker.code",
        read_only=True,
    )
    device_code = serializers.CharField(
        source="device.device_code",
        read_only=True,
    )
    reading_id = serializers.IntegerField(
        read_only=True,
    )
    arkl_result_id = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Alert
        fields = [
            "id",
            "worker_code",
            "device_code",
            "reading_id",
            "arkl_result_id",
            "concentration_ppm",
            "environmental_level",
            "environmental_status",
            "environmental_severity",
            "rq",
            "risk_interpretation",
            "calculation_version",
            "alert_level",
            "risk_status",
            "status",
            "recommendation_codes",
            "alert_rule_version",
            "source_simulated",
            "acknowledged_at",
            "resolved_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class AlertEvaluateRequestSerializer(serializers.Serializer):
    arkl_result_id = serializers.PrimaryKeyRelatedField(
        queryset=ARKLResult.objects.select_related(
            "worker",
            "reading",
            "reading__device",
        ),
        source="arkl_result",
    )


class AlertEvaluationResponseSerializer(serializers.Serializer):
    created = serializers.BooleanField()
    duplicate = serializers.BooleanField()
    escalated = serializers.BooleanField()
    alert = AlertSerializer(
        allow_null=True,
    )
