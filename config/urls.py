import time

from django.contrib import admin
from django.http import HttpResponse
from django.urls import path


def middleware_test_view(request):
    return HttpResponse("middleware-ok")


def middleware_slow_view(request):
    time.sleep(0.02)
    return HttpResponse("slow-ok")


urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "__test__/middleware/",
        middleware_test_view,
    ),

    path(
        "__test__/slow/",
        middleware_slow_view,
    ),
]