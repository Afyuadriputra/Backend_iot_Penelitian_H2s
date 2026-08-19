from django.contrib import admin

from exposure.models import ExposureProfile, Worker


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "is_active",
        "created_at",
        "updated_at",
    )

    search_fields = ("code",)

    list_filter = ("is_active",)


@admin.register(ExposureProfile)
class ExposureProfileAdmin(admin.ModelAdmin):
    list_display = (
        "worker",
        "body_weight",
        "exposure_time",
        "exposure_frequency",
        "exposure_duration",
        "inhalation_rate",
        "updated_at",
    )

    search_fields = ("worker__code",)
