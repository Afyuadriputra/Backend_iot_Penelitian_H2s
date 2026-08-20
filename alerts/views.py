from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
)
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from alerts.models import Alert
from alerts.serializers import (
    AlertEvaluateRequestSerializer,
    AlertEvaluationResponseSerializer,
    AlertSerializer,
)
from alerts.services.alert_service import (
    evaluate_realtime_arkl_alert,
)
from alerts.services.exceptions import (
    AlertLifecycleError,
    AlertValidationError,
)
from alerts.services.lifecycle import (
    acknowledge_alert,
    resolve_alert,
)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="worker_code",
            type=str,
            required=False,
        ),
        OpenApiParameter(
            name="device_code",
            type=str,
            required=False,
        ),
        OpenApiParameter(
            name="alert_level",
            type=str,
            required=False,
        ),
        OpenApiParameter(
            name="status",
            type=str,
            required=False,
        ),
    ],
)
class AlertListView(generics.ListAPIView):
    serializer_class = AlertSerializer

    def get_queryset(self):
        queryset = Alert.objects.select_related(
            "worker",
            "device",
            "reading",
            "arkl_result",
        )

        worker_code = self.request.query_params.get("worker_code")
        device_code = self.request.query_params.get("device_code")
        alert_level = self.request.query_params.get("alert_level")
        lifecycle_status = self.request.query_params.get("status")

        if worker_code:
            queryset = queryset.filter(worker__code=worker_code)

        if device_code:
            queryset = queryset.filter(device__device_code=device_code)

        if alert_level:
            queryset = queryset.filter(alert_level=alert_level)

        if lifecycle_status:
            queryset = queryset.filter(status=lifecycle_status)

        return queryset


class AlertDetailView(generics.RetrieveAPIView):
    serializer_class = AlertSerializer
    queryset = Alert.objects.select_related(
        "worker",
        "device",
        "reading",
        "arkl_result",
    )


class AlertEvaluateView(APIView):
    @extend_schema(
        request=AlertEvaluateRequestSerializer,
        responses={
            200: AlertEvaluationResponseSerializer,
            201: AlertEvaluationResponseSerializer,
        },
    )
    def post(self, request):
        serializer = AlertEvaluateRequestSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        arkl_result = serializer.validated_data[
            "arkl_result"
        ]

        try:
            result = evaluate_realtime_arkl_alert(
                arkl_result=arkl_result
            )
        except AlertValidationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = (
            AlertEvaluationResponseSerializer(result)
        )

        response_status = (
            status.HTTP_201_CREATED
            if result.created
            else status.HTTP_200_OK
        )

        return Response(
            response_serializer.data,
            status=response_status,
        )

class AlertAcknowledgeView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: AlertSerializer,
        },
    )
    def patch(self, request, pk):
        try:
            alert = Alert.objects.get(pk=pk)
        except Alert.DoesNotExist:
            return Response(
                {"detail": "Alert not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            alert = acknowledge_alert(alert)
        except AlertLifecycleError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            AlertSerializer(alert).data,
            status=status.HTTP_200_OK,
        )


class AlertResolveView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: AlertSerializer,
        },
    )
    def patch(self, request, pk):
        try:
            alert = Alert.objects.get(pk=pk)
        except Alert.DoesNotExist:
            return Response(
                {"detail": "Alert not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        alert = resolve_alert(alert)

        return Response(
            AlertSerializer(alert).data,
            status=status.HTTP_200_OK,
        )
