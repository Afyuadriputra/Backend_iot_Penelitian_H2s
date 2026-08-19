import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from exposure.models import ExposureProfile, Worker
from exposure.services.validation import (
    ExposureValidationError,
    validate_exposure_data,
)


@pytest.mark.django_db
def test_worker_can_be_created():
    worker = Worker.objects.create(
        code="PML-001",
    )

    assert worker.pk is not None
    assert worker.code == "PML-001"
    assert worker.is_active is True


@pytest.mark.django_db
def test_worker_code_must_be_unique():
    Worker.objects.create(
        code="PML-001",
    )

    with pytest.raises(IntegrityError):
        Worker.objects.create(
            code="PML-001",
        )


@pytest.mark.django_db
def test_exposure_profile_can_be_created():
    worker = Worker.objects.create(
        code="PML-001",
    )

    profile = ExposureProfile.objects.create(
        worker=worker,
        body_weight=55.0,
        exposure_time=8.0,
        exposure_frequency=250.0,
        exposure_duration=10.0,
        inhalation_rate=0.83,
    )

    assert profile.pk is not None
    assert profile.worker == worker
    assert profile.body_weight == 55.0


@pytest.mark.django_db
def test_worker_has_one_exposure_profile():
    worker = Worker.objects.create(
        code="PML-001",
    )

    ExposureProfile.objects.create(
        worker=worker,
        body_weight=55.0,
        exposure_time=8.0,
        exposure_frequency=250.0,
        exposure_duration=10.0,
        inhalation_rate=0.83,
    )

    assert worker.exposure_profile.body_weight == 55.0


@pytest.mark.django_db
def test_worker_cannot_have_duplicate_exposure_profile():
    worker = Worker.objects.create(
        code="PML-001",
    )

    ExposureProfile.objects.create(
        worker=worker,
        body_weight=55.0,
        exposure_time=8.0,
        exposure_frequency=250.0,
        exposure_duration=10.0,
        inhalation_rate=0.83,
    )

    with pytest.raises(IntegrityError):
        ExposureProfile.objects.create(
            worker=worker,
            body_weight=60.0,
            exposure_time=8.0,
            exposure_frequency=250.0,
            exposure_duration=10.0,
            inhalation_rate=0.83,
        )


def test_valid_exposure_data():
    result = validate_exposure_data(
        body_weight=55,
        exposure_time=8,
        exposure_frequency=250,
        exposure_duration=10,
        inhalation_rate=0.83,
    )

    assert result.body_weight == 55.0
    assert result.exposure_time == 8.0


def test_body_weight_zero_is_rejected():
    with pytest.raises(
        ExposureValidationError,
        match="body_weight must be greater than zero",
    ):
        validate_exposure_data(
            body_weight=0,
            exposure_time=8,
            exposure_frequency=250,
            exposure_duration=10,
            inhalation_rate=0.83,
        )


def test_negative_exposure_time_is_rejected():
    with pytest.raises(
        ExposureValidationError,
        match="exposure_time cannot be negative",
    ):
        validate_exposure_data(
            body_weight=55,
            exposure_time=-1,
            exposure_frequency=250,
            exposure_duration=10,
            inhalation_rate=0.83,
        )


@pytest.mark.django_db
def test_model_validation_rejects_negative_body_weight():
    worker = Worker.objects.create(
        code="PML-001",
    )

    profile = ExposureProfile(
        worker=worker,
        body_weight=-10,
        exposure_time=8,
        exposure_frequency=250,
        exposure_duration=10,
        inhalation_rate=0.83,
    )

    with pytest.raises(ValidationError):
        profile.full_clean()


@pytest.mark.django_db
def test_worker_can_be_created_via_api(client):
    response = client.post(
        "/api/v1/workers/",
        data={
            "code": "PML-API-001",
        },
        content_type="application/json",
    )

    assert response.status_code == 201

    assert Worker.objects.filter(code="PML-API-001").exists()


@pytest.mark.django_db
def test_exposure_profile_can_be_created_via_api(client):
    worker = Worker.objects.create(code="PML-001")

    response = client.post(
        "/api/v1/exposure-profiles/",
        data={
            "worker": worker.pk,
            "body_weight": 55,
            "exposure_time": 8,
            "exposure_frequency": 250,
            "exposure_duration": 10,
            "inhalation_rate": 0.83,
        },
        content_type="application/json",
    )

    assert response.status_code == 201
    assert ExposureProfile.objects.count() == 1


@pytest.mark.django_db
def test_exposure_profile_can_be_patched(client):
    worker = Worker.objects.create(code="PML-001")

    profile = ExposureProfile.objects.create(
        worker=worker,
        body_weight=55,
        exposure_time=8,
        exposure_frequency=250,
        exposure_duration=10,
        inhalation_rate=0.83,
    )

    response = client.patch(
        f"/api/v1/exposure-profiles/{profile.pk}/",
        data={
            "body_weight": 60,
        },
        content_type="application/json",
    )

    assert response.status_code == 200

    profile.refresh_from_db()

    assert profile.body_weight == 60


@pytest.mark.django_db
def test_invalid_exposure_returns_400(client):
    worker = Worker.objects.create(code="PML-001")

    response = client.post(
        "/api/v1/exposure-profiles/",
        data={
            "worker": worker.pk,
            "body_weight": -1,
            "exposure_time": 8,
            "exposure_frequency": 250,
            "exposure_duration": 10,
            "inhalation_rate": 0.83,
        },
        content_type="application/json",
    )

    assert response.status_code == 400
