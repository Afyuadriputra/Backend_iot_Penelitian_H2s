# Create your views here.
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from devices.models import Device, H2SReading
from devices.serializers import (
    DeviceSerializer,
    H2SReadingSerializer,
)


class DeviceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


class H2SReadingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = H2SReadingSerializer

    def get_queryset(self):
        queryset = H2SReading.objects.select_related("device").all()

        device_code = self.request.query_params.get("device_code")
        status_value = self.request.query_params.get("status")

        if device_code:
            queryset = queryset.filter(device__device_code=device_code)

        if status_value:
            queryset = queryset.filter(status=status_value)

        return queryset

    @action(
        detail=False,
        methods=["get"],
        url_path="latest",
    )
    def latest(self, request):
        reading = self.get_queryset().first()

        if reading is None:
            return Response(
                {"detail": "No H2S reading available."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(reading)

        return Response(serializer.data)
