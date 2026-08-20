from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from alerts.models import Alert
from alerts.services.constants import (
    AlertLevel,
    AlertLifecycleStatus,
)
from arkl.models import ARKLResult
from devices.models import Device, H2SReading
from exposure.models import ExposureProfile, Worker


@pytest.mark.django_db
def test_realtime_arkl_to_alert_full_e2e():
    worker = Worker.objects.create(
        code="PML-E2E-ALERT-001",
        is_active=True,
    )

    ExposureProfile.objects.create(
        worker=worker,
        body_weight=55,
        exposure_time=8,
        exposure_frequency=250,
        exposure_duration=10,
        inhalation_rate=0.83,
    )

    device = Device.objects.create(
        device_code="H2S-E2E-ALERT-001",
        name="E2E Alert Device",
        location="TPA Test",
        is_active=True,
    )

    reading = H2SReading.objects.create(
        device=device,
        ppm=25.4,
        adc=1000,
        filtered_adc=1000,
        level=2,
        status="WARNING",
        uptime_ms=1000,
        simulated=True,
    )

    arkl_result = ARKLResult.objects.create(
        worker=worker,
        reading=reading,
        calculation_type="REALTIME",
        concentration_ppm=Decimal("25.400000"),
        concentration_mg_m3=Decimal("35.560000"),
        exposure_concentration_mg_m3=Decimal("8.118721"),
        body_weight=Decimal("55"),
        exposure_time=Decimal("8"),
        exposure_frequency=Decimal("250"),
        exposure_duration=Decimal("10"),
        inhalation_rate=Decimal("0.83"),
        averaging_time=None,
        intake=None,
        rfc=Decimal("0.002"),
        rq=Decimal("4059.360730593607"),
        interpretation="ABOVE_REFERENCE_LEVEL",
        calculation_version="1.1.0-MVP",
        source_simulated=True,
    )

    client = APIClient()

    # 1. Evaluate
    response = client.post(
        "/api/v1/alerts/evaluate/",
        {
            "arkl_result_id": arkl_result.id,
        },
        format="json",
    )

    assert response.status_code == 201

    payload = response.json()

    assert payload["created"] is True
    assert payload["duplicate"] is False
    assert payload["escalated"] is False

    alert_data = payload["alert"]

    assert alert_data["worker_code"] == worker.code
    assert alert_data["device_code"] == device.device_code
    assert alert_data["reading_id"] == reading.id
    assert alert_data["arkl_result_id"] == arkl_result.id

    assert alert_data["environmental_status"] == "WARNING"
    assert alert_data["environmental_severity"] == "WARNING"

    assert alert_data["risk_interpretation"] == "ABOVE_REFERENCE_LEVEL"

    assert alert_data["alert_level"] == AlertLevel.HIGH
    assert alert_data["status"] == AlertLifecycleStatus.OPEN

    assert alert_data["source_simulated"] is True
    assert len(alert_data["recommendation_codes"]) > 0

    alert_id = alert_data["id"]

    # 2. Persistence
    assert Alert.objects.count() == 1

    alert = Alert.objects.get(pk=alert_id)

    assert alert.reading_id == reading.id
    assert alert.arkl_result_id == arkl_result.id
    assert alert.alert_level == AlertLevel.HIGH

    # 3. Duplicate protection
    duplicate_response = client.post(
        "/api/v1/alerts/evaluate/",
        {
            "arkl_result_id": arkl_result.id,
        },
        format="json",
    )

    assert duplicate_response.status_code == 200

    duplicate_payload = duplicate_response.json()

    assert duplicate_payload["created"] is False
    assert duplicate_payload["duplicate"] is True

    assert Alert.objects.count() == 1

    # 4. Retrieve
    detail_response = client.get(f"/api/v1/alerts/{alert_id}/")

    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == alert_id

    # 5. Acknowledge
    acknowledge_response = client.patch(
        f"/api/v1/alerts/{alert_id}/acknowledge/",
        data={},
        format="json",
    )

    assert acknowledge_response.status_code == 200
    assert acknowledge_response.json()["status"] == AlertLifecycleStatus.ACKNOWLEDGED

    # 6. Acknowledged alert still deduplicates
    duplicate_after_ack = client.post(
        "/api/v1/alerts/evaluate/",
        {
            "arkl_result_id": arkl_result.id,
        },
        format="json",
    )

    assert duplicate_after_ack.status_code == 200
    assert duplicate_after_ack.json()["duplicate"] is True
    assert Alert.objects.count() == 1

    # 7. Resolve
    resolve_response = client.patch(
        f"/api/v1/alerts/{alert_id}/resolve/",
        data={},
        format="json",
    )

    assert resolve_response.status_code == 200
    assert resolve_response.json()["status"] == AlertLifecycleStatus.RESOLVED

    alert.refresh_from_db()

    assert alert.status == AlertLifecycleStatus.RESOLVED
    assert alert.resolved_at is not None
