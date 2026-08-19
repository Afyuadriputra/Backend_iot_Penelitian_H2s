from rest_framework import mixins, viewsets

from exposure.models import ExposureProfile, Worker
from exposure.serializers import (
    ExposureProfileSerializer,
    WorkerSerializer,
)


class WorkerViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer


class ExposureProfileViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ExposureProfile.objects.select_related("worker")
    serializer_class = ExposureProfileSerializer

    http_method_names = [
        "get",
        "post",
        "patch",
        "head",
        "options",
    ]
