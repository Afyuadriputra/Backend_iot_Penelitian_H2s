from django.urls import path

from arkl.views import (
    ARKLResultDetailView,
    ARKLResultListView,
    HistoricalARKLView,
    RealtimeARKLView,
)

urlpatterns = [
    path(
        "arkl/realtime/",
        RealtimeARKLView.as_view(),
        name="arkl-realtime",
    ),
    path(
        "arkl/historical/",
        HistoricalARKLView.as_view(),
        name="arkl-historical",
    ),
    path(
        "arkl/results/",
        ARKLResultListView.as_view(),
        name="arkl-result-list",
    ),
    path(
        "arkl/results/<int:pk>/",
        ARKLResultDetailView.as_view(),
        name="arkl-result-detail",
    ),
]
