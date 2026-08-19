from django.contrib import admin

from arkl.models import ARKLResult


@admin.register(ARKLResult)
class ARKLResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "worker",
        "calculation_type",
        "concentration_ppm",
        "rq",
        "interpretation",
        "source_simulated",
        "calculation_version",
        "created_at",
    )

    list_filter = (
        "calculation_type",
        "interpretation",
        "source_simulated",
        "calculation_version",
    )

    search_fields = (
        "worker__code",
        "reading__device__device_code",
    )

    readonly_fields = ("created_at",)
