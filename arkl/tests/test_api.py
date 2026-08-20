from datetime import timedelta

import pytest
from django.utils import timezone

from arkl.models import ARKLResult
from devices.models import Device, H2SReading
from exposure.models import ExposureProfile, Worker


def create_worker_with_profile(
    code="PML-API-001",
):
    worker = Worker.objects.create(
        code=code,
    )

    ExposureProfile.objects.create(
        worker=worker,
        body_weight=55,
        exposure_time=8,
        exposure_frequency=250,
        exposure_duration=10,
        inhalation_rate=0.83,
    )

    return worker


def create_device_with_reading(
    code="H2S-API-001",
    ppm=10,
):
    device = Device.objects.create(
        device_code=code,
    )

    reading = H2SReading.objects.create(
        device=device,
        ppm=ppm,
        adc=500,
        filtered_adc=500,
        level=2,
        status="TEST",
        uptime_ms=1000,
        simulated=True,
    )

    return device, reading


@pytest.mark.django_db
def test_realtime_arkl_api_creates_result(client):
    worker = create_worker_with_profile()
    device, reading = create_device_with_reading()

    response = client.post(
        "/api/v1/arkl/realtime/",
        data={
            "worker": worker.pk,
            "device": device.pk,
        },
        content_type="application/json",
    )

    assert response.status_code == 201

    data = response.json()

    assert data["calculation_type"] == "REALTIME"
    assert data["worker"] == worker.pk
    assert data["reading"] == reading.pk

    assert data["concentration_ppm"] is not None
    assert data["concentration_mg_m3"] is not None

    # ARKL v2 no longer uses exposure concentration
    # as the primary RQ calculation.
    assert data["exposure_concentration_mg_m3"] is None

    # Intake-based ARKL output.
    assert float(data["averaging_time"]) > 0
    assert float(data["intake"]) > 0
    assert float(data["rq"]) > 0

    assert data["calculation_version"] == "2.0.0-MVP"

    assert data["interpretation"] in {
        "WITHIN_REFERENCE_LEVEL",
        "ABOVE_REFERENCE_LEVEL",
    }

    assert data["source_simulated"] is True

    assert ARKLResult.objects.count() == 1


@pytest.mark.django_db
def test_realtime_api_ignores_client_calculated_values(
    client,
):
    worker = create_worker_with_profile(
        code="PML-CLIENT-CALC",
    )

    device, _ = create_device_with_reading(
        code="H2S-CLIENT-CALC",
        ppm=10,
    )

    response = client.post(
        "/api/v1/arkl/realtime/",
        data={
            "worker": worker.pk,
            "device": device.pk,

            # Values below must be ignored because
            # calculation happens on the backend.
            "rq": 0,
            "intake": 0,
            "averaging_time": 0,
            "exposure_concentration_mg_m3": 999999,
            "interpretation": "WITHIN_REFERENCE_LEVEL",
            "calculation_version": "CLIENT-FAKE-VERSION",
        },
        content_type="application/json",
    )

    assert response.status_code == 201

    data = response.json()

    assert float(data["rq"]) > 0
    assert float(data["intake"]) > 0
    assert float(data["averaging_time"]) > 0

    assert data["exposure_concentration_mg_m3"] is None

    assert data["calculation_version"] == "2.0.0-MVP"

    assert data["calculation_version"] != "CLIENT-FAKE-VERSION"


@pytest.mark.django_db
def test_realtime_api_without_exposure_profile_returns_400(
    client,
):
    worker = Worker.objects.create(
        code="PML-NO-PROFILE-API",
    )

    device, _ = create_device_with_reading(
        code="H2S-NO-PROFILE-API",
    )

    response = client.post(
        "/api/v1/arkl/realtime/",
        data={
            "worker": worker.pk,
            "device": device.pk,
        },
        content_type="application/json",
    )

    assert response.status_code == 400

    assert (
        "exposure profile"
        in response.json()["detail"].lower()
    )


@pytest.mark.django_db
def test_realtime_api_invalid_worker_returns_400(
    client,
):
    device, _ = create_device_with_reading(
        code="H2S-BAD-WORKER",
    )

    response = client.post(
        "/api/v1/arkl/realtime/",
        data={
            "worker": 999999,
            "device": device.pk,
        },
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "worker" in response.json()


@pytest.mark.django_db
def test_realtime_api_invalid_device_returns_400(
    client,
):
    worker = create_worker_with_profile(
        code="PML-BAD-DEVICE",
    )

    response = client.post(
        "/api/v1/arkl/realtime/",
        data={
            "worker": worker.pk,
            "device": 999999,
        },
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "device" in response.json()


@pytest.mark.django_db
def test_historical_arkl_api_creates_result(
    client,
):
    worker = create_worker_with_profile(
        code="PML-HIST-API",
    )

    device = Device.objects.create(
        device_code="H2S-HIST-API",
    )

    now = timezone.now()
    readings = []

    for ppm in [10, 20, 30]:
        reading = H2SReading.objects.create(
            device=device,
            ppm=ppm,
            adc=100,
            filtered_adc=100,
            level=1,
            status="TEST",
            uptime_ms=1000,
            simulated=True,
        )

        readings.append(reading)

    for index, reading in enumerate(readings):
        timestamp = now - timedelta(
            minutes=30 - (index * 10)
        )

        H2SReading.objects.filter(
            pk=reading.pk,
        ).update(
            received_at=timestamp,
        )

    response = client.post(
        "/api/v1/arkl/historical/",
        data={
            "worker": worker.pk,
            "device": device.pk,
            "start_time": (
                now - timedelta(hours=1)
            ).isoformat(),
            "end_time": now.isoformat(),
        },
        content_type="application/json",
    )

    assert response.status_code == 201

    data = response.json()

    assert data["calculation_type"] == "HISTORICAL"
    assert data["reading"] is None
    assert data["reading_count"] == 3

    assert float(data["concentration_ppm"]) == 20.0
    assert float(data["concentration_mg_m3"]) == 28.0

    assert data["exposure_concentration_mg_m3"] is None

    assert float(data["averaging_time"]) > 0
    assert float(data["intake"]) > 0
    assert float(data["rq"]) > 0

    assert data["calculation_version"] == "2.0.0-MVP"
    assert data["source_simulated"] is True


@pytest.mark.django_db
def test_historical_api_invalid_period_returns_400(
    client,
):
    worker = create_worker_with_profile(
        code="PML-HIST-BAD-PERIOD",
    )

    device = Device.objects.create(
        device_code="H2S-HIST-BAD-PERIOD",
    )

    now = timezone.now()

    response = client.post(
        "/api/v1/arkl/historical/",
        data={
            "worker": worker.pk,
            "device": device.pk,
            "start_time": now.isoformat(),
            "end_time": now.isoformat(),
        },
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "end_time" in response.json()


@pytest.mark.django_db
def test_historical_api_without_readings_returns_400(
    client,
):
    worker = create_worker_with_profile(
        code="PML-HIST-EMPTY-API",
    )

    device = Device.objects.create(
        device_code="H2S-HIST-EMPTY-API",
    )

    now = timezone.now()

    response = client.post(
        "/api/v1/arkl/historical/",
        data={
            "worker": worker.pk,
            "device": device.pk,
            "start_time": (
                now - timedelta(hours=1)
            ).isoformat(),
            "end_time": now.isoformat(),
        },
        content_type="application/json",
    )

    assert response.status_code == 400

    assert (
        "no h2s readings"
        in response.json()["detail"].lower()
    )


@pytest.mark.django_db
def test_arkl_result_list_api(
    client,
):
    worker = create_worker_with_profile(
        code="PML-LIST-API",
    )

    device, _ = create_device_with_reading(
        code="H2S-LIST-API",
    )

    create_response = client.post(
        "/api/v1/arkl/realtime/",
        data={
            "worker": worker.pk,
            "device": device.pk,
        },
        content_type="application/json",
    )

    assert create_response.status_code == 201

    response = client.get(
        "/api/v1/arkl/results/"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert len(data["results"]) == 1

    result = data["results"][0]

    assert result["calculation_version"] == "2.0.0-MVP"
    assert result["intake"] is not None
    assert result["averaging_time"] is not None


@pytest.mark.django_db
def test_arkl_result_detail_api(
    client,
):
    worker = create_worker_with_profile(
        code="PML-DETAIL-API",
    )

    device, _ = create_device_with_reading(
        code="H2S-DETAIL-API",
    )

    create_response = client.post(
        "/api/v1/arkl/realtime/",
        data={
            "worker": worker.pk,
            "device": device.pk,
        },
        content_type="application/json",
    )

    assert create_response.status_code == 201

    result_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/arkl/results/{result_id}/"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == result_id
    assert data["calculation_type"] == "REALTIME"
    assert data["calculation_version"] == "2.0.0-MVP"

    assert data["exposure_concentration_mg_m3"] is None
    assert data["intake"] is not None
    assert data["averaging_time"] is not None


@pytest.mark.django_db
def test_arkl_result_filter_by_worker_code(
    client,
):
    worker = create_worker_with_profile(
        code="PML-FILTER-001",
    )

    device, _ = create_device_with_reading(
        code="H2S-FILTER-001",
    )

    create_response = client.post(
        "/api/v1/arkl/realtime/",
        data={
            "worker": worker.pk,
            "device": device.pk,
        },
        content_type="application/json",
    )

    assert create_response.status_code == 201

    response = client.get(
        "/api/v1/arkl/results/"
        "?worker_code=PML-FILTER-001"
    )

    assert response.status_code == 200
    assert response.json()["count"] == 1


@pytest.mark.django_db
def test_arkl_result_filter_by_calculation_type(
    client,
):
    worker = create_worker_with_profile(
        code="PML-TYPE-FILTER",
    )

    device, _ = create_device_with_reading(
        code="H2S-TYPE-FILTER",
    )

    create_response = client.post(
        "/api/v1/arkl/realtime/",
        data={
            "worker": worker.pk,
            "device": device.pk,
        },
        content_type="application/json",
    )

    assert create_response.status_code == 201

    response = client.get(
        "/api/v1/arkl/results/"
        "?calculation_type=REALTIME"
    )

    assert response.status_code == 200
    assert response.json()["count"] == 1