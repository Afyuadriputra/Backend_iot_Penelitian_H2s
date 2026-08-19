import json

import pytest
from django.db import IntegrityError

from devices.models import Device, H2SReading
from devices.services.mqtt_ingestion import (
    ingest_mqtt_message,
)
from devices.services.telemetry import (
    TelemetryValidationError,
    validate_telemetry_payload,
)


@pytest.mark.django_db
def test_device_can_be_created():
    device = Device.objects.create(
        device_code="H2S-TPA-001",
        name="H2S Simulator",
        location="Wokwi",
    )

    assert device.pk is not None
    assert device.device_code == "H2S-TPA-001"
    assert device.is_active is True


@pytest.mark.django_db
def test_device_code_must_be_unique():
    Device.objects.create(
        device_code="H2S-TPA-001",
    )

    with pytest.raises(IntegrityError):
        Device.objects.create(
            device_code="H2S-TPA-001",
        )


@pytest.mark.django_db
def test_h2s_reading_can_be_stored():
    device = Device.objects.create(
        device_code="H2S-TPA-001",
    )

    reading = H2SReading.objects.create(
        device=device,
        ppm=12.45,
        adc=850,
        filtered_adc=848.3,
        level=3,
        status="WARNING",
        uptime_ms=120000,
        simulated=True,
    )

    assert reading.pk is not None

    assert reading.device == device
    assert reading.ppm == 12.45
    assert reading.adc == 850
    assert reading.filtered_adc == 848.3
    assert reading.level == 3
    assert reading.status == "WARNING"
    assert reading.uptime_ms == 120000
    assert reading.simulated is True
    assert reading.received_at is not None


@pytest.mark.django_db
def test_device_readings_relationship():
    device = Device.objects.create(
        device_code="H2S-TPA-001",
    )

    H2SReading.objects.create(
        device=device,
        ppm=1.0,
        adc=100,
        filtered_adc=100.0,
        level=1,
        status="NORMAL",
        uptime_ms=1000,
        simulated=True,
    )

    H2SReading.objects.create(
        device=device,
        ppm=2.0,
        adc=200,
        filtered_adc=200.0,
        level=2,
        status="WARNING",
        uptime_ms=2000,
        simulated=True,
    )

    assert device.readings.count() == 2


def valid_payload():
    return {
        "device_id": "H2S-TPA-001",
        "ppm": 12.45,
        "adc": 850,
        "filtered_adc": 848.3,
        "level": 3,
        "status": "WARNING",
        "uptime_ms": 120000,
        "simulated": True,
    }


def test_valid_telemetry_payload():
    data = validate_telemetry_payload(valid_payload())

    assert data.device_id == "H2S-TPA-001"
    assert data.ppm == 12.45
    assert data.adc == 850
    assert data.simulated is True


def test_missing_telemetry_field_is_rejected():
    payload = valid_payload()

    del payload["ppm"]

    with pytest.raises(
        TelemetryValidationError,
        match="Missing required field",
    ):
        validate_telemetry_payload(payload)


def test_negative_ppm_is_rejected():
    payload = valid_payload()
    payload["ppm"] = -1

    with pytest.raises(
        TelemetryValidationError,
        match="ppm cannot be negative",
    ):
        validate_telemetry_payload(payload)


def test_adc_out_of_range_is_rejected():
    payload = valid_payload()
    payload["adc"] = 5000

    with pytest.raises(
        TelemetryValidationError,
        match="adc must be between",
    ):
        validate_telemetry_payload(payload)


def test_simulated_must_be_boolean():
    payload = valid_payload()
    payload["simulated"] = "true"

    with pytest.raises(
        TelemetryValidationError,
        match="simulated must be boolean",
    ):
        validate_telemetry_payload(payload)


@pytest.mark.django_db
def test_valid_mqtt_payload_is_stored():
    payload = valid_payload()

    reading = ingest_mqtt_message(
        topic="test/topic",
        raw_payload=json.dumps(payload),
    )

    assert reading is not None

    assert H2SReading.objects.count() == 1
    assert Device.objects.count() == 1

    saved = H2SReading.objects.get()

    assert saved.ppm == 12.45
    assert saved.device.device_code == "H2S-TPA-001"


@pytest.mark.django_db
def test_invalid_json_is_not_stored():
    reading = ingest_mqtt_message(
        topic="test/topic",
        raw_payload="{invalid-json}",
    )

    assert reading is None
    assert H2SReading.objects.count() == 0


@pytest.mark.django_db
def test_invalid_payload_is_not_stored():
    payload = valid_payload()

    del payload["ppm"]

    reading = ingest_mqtt_message(
        topic="test/topic",
        raw_payload=json.dumps(payload),
    )

    assert reading is None
    assert H2SReading.objects.count() == 0


@pytest.mark.django_db
def test_existing_device_is_reused():
    Device.objects.create(
        device_code="H2S-TPA-001",
    )

    ingest_mqtt_message(
        topic="test/topic",
        raw_payload=json.dumps(valid_payload()),
    )

    assert Device.objects.count() == 1
    assert H2SReading.objects.count() == 1


@pytest.mark.django_db
def test_latest_reading_api(client):
    device = Device.objects.create(
        device_code="H2S-TPA-001",
    )

    H2SReading.objects.create(
        device=device,
        ppm=12.45,
        adc=850,
        filtered_adc=848.3,
        level=3,
        status="WARNING",
        uptime_ms=120000,
        simulated=True,
    )

    response = client.get("/api/v1/readings/latest/")

    assert response.status_code == 200

    data = response.json()

    assert data["device_code"] == "H2S-TPA-001"
    assert data["ppm"] == 12.45


@pytest.mark.django_db
def test_reading_list_is_paginated(client):
    device = Device.objects.create(
        device_code="H2S-TPA-001",
    )

    for index in range(3):
        H2SReading.objects.create(
            device=device,
            ppm=float(index),
            adc=index,
            filtered_adc=float(index),
            level=0,
            status="NORMAL",
            uptime_ms=index,
            simulated=True,
        )

    response = client.get("/api/v1/readings/")

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "results" in data
    assert data["count"] == 3
