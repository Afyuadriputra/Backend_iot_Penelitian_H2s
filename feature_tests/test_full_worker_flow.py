from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.models import AccountProfile
from alerts.models import Alert
from alerts.services.constants import (
    AlertLifecycleStatus,
)
from arkl.models import ARKLResult
from devices.models import Device, H2SReading
from exposure.models import (
    ExposureProfile,
    Worker,
)


User = get_user_model()


def create_operator_client():
    user = User.objects.create_user(
        username="feature-operator",
        password="StrongPass123!",
    )

    AccountProfile.objects.create(
        user=user,
        role=AccountProfile.Role.OPERATOR,
    )

    token = Token.objects.create(
        user=user,
    )

    client = APIClient()

    client.credentials(
        HTTP_AUTHORIZATION=(
            f"Token {token.key}"
        )
    )

    return client


def create_worker_client(worker):
    user = User.objects.create_user(
        username=f"worker-{worker.code}",
        password="StrongPass123!",
    )

    AccountProfile.objects.create(
        user=user,
        role=AccountProfile.Role.WORKER,
        worker=worker,
    )

    token = Token.objects.create(
        user=user,
    )

    client = APIClient()

    client.credentials(
        HTTP_AUTHORIZATION=(
            f"Token {token.key}"
        )
    )

    return client


@pytest.mark.django_db
def test_full_worker_h2s_risk_flow():
    # ========================================================
    # STEP 1 — DATA PEMULUNG
    # ========================================================

    worker = Worker.objects.create(
        code="PML-FEATURE-001",
        name="Budi",
        age=41,
        is_active=True,
    )

    exposure = ExposureProfile.objects.create(
        worker=worker,
        body_weight=55,
        exposure_time=8,
        exposure_frequency=250,
        exposure_duration=10,
        inhalation_rate=Decimal("0.83"),
    )

    assert worker.name == "Budi"
    assert worker.age == 41
    assert worker.is_active is True

    assert exposure.body_weight == 55
    assert exposure.exposure_time == 8
    assert exposure.exposure_frequency == 250
    assert exposure.exposure_duration == 10

    # ========================================================
    # STEP 2 — SENSOR H2S
    # ========================================================

    device = Device.objects.create(
        device_code="H2S-FEATURE-001",
        name="Sensor TPA Muara Fajar",
        location="Zona Pemilahan",
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

    assert float(reading.ppm) == 25.4
    assert reading.status == "WARNING"
    assert reading.simulated is True

    # ========================================================
    # STEP 3 — OPERATOR MENJALANKAN ARKL
    # ========================================================

    operator_client = (
        create_operator_client()
    )

    response = operator_client.post(
        "/api/v1/arkl/realtime/",
        {
            "worker": worker.pk,
            "device": device.pk,
        },
        format="json",
    )

    assert response.status_code == 201

    arkl_data = response.json()

    # ========================================================
    # STEP 4 — VERIFIKASI FORMULA
    # ========================================================

    expected_c = (
        Decimal("25.4")
        * Decimal("1.40")
    )

    expected_tavg = (
        Decimal("10")
        * Decimal("365")
    )

    expected_intake = (
        expected_c
        * Decimal("0.83")
        * Decimal("8")
        * Decimal("250")
        * Decimal("10")
        / (
            Decimal("55")
            * expected_tavg
        )
    )

    expected_rq = (
        expected_intake
        / Decimal("0.002")
    )

    assert (
        Decimal(
            str(
                arkl_data[
                    "concentration_mg_m3"
                ]
            )
        )
        == expected_c
    )

    assert (
        Decimal(
            str(
                arkl_data[
                    "averaging_time"
                ]
            )
        )
        == expected_tavg
    )

    actual_intake = Decimal(
        str(arkl_data["intake"])
    )

    actual_rq = Decimal(
        str(arkl_data["rq"])
    )

    assert (
        abs(
            actual_intake
            - expected_intake
        )
        < Decimal("0.000001")
    )

    assert (
        abs(
            actual_rq
            - expected_rq
        )
        < Decimal("0.01")
    )

    assert (
        arkl_data["interpretation"]
        == "ABOVE_REFERENCE_LEVEL"
    )

    assert (
        arkl_data[
            "calculation_version"
        ]
        == "2.0.0-MVP"
    )

    # ========================================================
    # STEP 5 — ARKL RESULT BENAR-BENAR TERSIMPAN
    # ========================================================

    arkl_result = ARKLResult.objects.get(
        pk=arkl_data["id"]
    )

    assert arkl_result.worker == worker
    assert arkl_result.reading == reading
    assert arkl_result.source_simulated is True

    # ========================================================
    # STEP 6 — ALERT EVALUATION
    # ========================================================

    response = operator_client.post(
        "/api/v1/alerts/evaluate/",
        {
            "arkl_result_id": (
                arkl_result.pk
            ),
        },
        format="json",
    )

    assert response.status_code == 201

    payload = response.json()

    assert payload["created"] is True
    assert payload["duplicate"] is False

    alert_data = payload["alert"]

    assert (
        alert_data[
            "environmental_status"
        ]
        == "WARNING"
    )

    assert (
        alert_data[
            "risk_interpretation"
        ]
        == "ABOVE_REFERENCE_LEVEL"
    )

    # Sesuai matrix core backend saat ini:
    assert (
        alert_data["alert_level"]
        == "HIGH"
    )

    assert (
        alert_data["risk_status"]
        == "RISK_MANAGEMENT_REQUIRED"
    )

    assert (
        alert_data["status"]
        == AlertLifecycleStatus.OPEN
    )

    assert (
        len(
            alert_data[
                "recommendation_codes"
            ]
        )
        > 0
    )

    # ========================================================
    # STEP 7 — PERSISTENCE ALERT
    # ========================================================

    alert = Alert.objects.get(
        pk=alert_data["id"]
    )

    assert alert.worker == worker
    assert alert.device == device
    assert alert.reading == reading
    assert (
        alert.arkl_result
        == arkl_result
    )

    assert alert.alert_level == "HIGH"

    # ========================================================
    # STEP 8 — WORKER LOGIN
    # ========================================================

    worker_client = (
        create_worker_client(worker)
    )

    # ========================================================
    # STEP 9 — WORKER MELIHAT ARKL MILIK SENDIRI
    # ========================================================

    response = worker_client.get(
        "/api/v1/me/arkl-results/"
    )

    assert response.status_code == 200

    data = response.json()

    results = (
        data["results"]
        if isinstance(data, dict)
        and "results" in data
        else data
    )

    assert len(results) == 1

    assert (
        results[0]["id"]
        == arkl_result.id
    )

    # ========================================================
    # STEP 10 — WORKER MELIHAT ALERT MILIK SENDIRI
    # ========================================================

    response = worker_client.get(
        "/api/v1/me/alerts/"
    )

    assert response.status_code == 200

    data = response.json()

    results = (
        data["results"]
        if isinstance(data, dict)
        and "results" in data
        else data
    )

    assert len(results) == 1

    worker_alert = results[0]

    assert (
        worker_alert["id"]
        == alert.id
    )

    assert (
        worker_alert["alert_level"]
        == "HIGH"
    )

    # ========================================================
    # STEP 11 — WORKER TIDAK BOLEH MELIHAT GENERIC ALERT
    # ========================================================

    response = worker_client.get(
        "/api/v1/alerts/"
    )

    assert response.status_code == 403