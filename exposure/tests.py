import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.models import AccountProfile
from exposure.models import ExposureProfile, Worker
from exposure.services.validation import (
    ExposureValidationError,
    validate_exposure_data,
)


User = get_user_model()


# ============================================================
# WORKER MODEL
# ============================================================


@pytest.mark.django_db
def test_worker_can_be_created():
    """
    Existing/internal Worker records remain compatible
    even when identity fields are not populated yet.
    """

    worker = Worker.objects.create(
        code="PML-001",
    )

    assert worker.pk is not None
    assert worker.code == "PML-001"
    assert worker.name is None
    assert worker.age is None
    assert worker.is_active is True


@pytest.mark.django_db
def test_worker_identity_can_be_stored():
    worker = Worker.objects.create(
        code="PML-IDENTITY-001",
        name="Sudirman",
        age=45,
    )

    assert worker.name == "Sudirman"
    assert worker.age == 45
    assert str(worker) == (
        "PML-IDENTITY-001 - Sudirman"
    )


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
def test_worker_model_rejects_invalid_age():
    worker = Worker(
        code="PML-INVALID-AGE",
        name="Ahmad",
        age=0,
    )

    with pytest.raises(ValidationError):
        worker.full_clean()


# ============================================================
# EXPOSURE PROFILE MODEL
# ============================================================


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
    assert profile.exposure_time == 8.0
    assert profile.exposure_frequency == 250.0
    assert profile.exposure_duration == 10.0
    assert profile.inhalation_rate == 0.83


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

    assert (
        worker.exposure_profile.body_weight
        == 55.0
    )


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
def test_model_validation_rejects_exposure_time_above_24():
    worker = Worker.objects.create(
        code="PML-TIME-MODEL",
    )

    profile = ExposureProfile(
        worker=worker,
        body_weight=55,
        exposure_time=25,
        exposure_frequency=250,
        exposure_duration=10,
        inhalation_rate=0.83,
    )

    with pytest.raises(ValidationError):
        profile.full_clean()


@pytest.mark.django_db
def test_model_validation_rejects_frequency_above_365():
    worker = Worker.objects.create(
        code="PML-FREQ-MODEL",
    )

    profile = ExposureProfile(
        worker=worker,
        body_weight=55,
        exposure_time=8,
        exposure_frequency=366,
        exposure_duration=10,
        inhalation_rate=0.83,
    )

    with pytest.raises(ValidationError):
        profile.full_clean()


# ============================================================
# EXPOSURE DOMAIN VALIDATION
# ============================================================


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
    assert result.exposure_frequency == 250.0
    assert result.exposure_duration == 10.0
    assert result.inhalation_rate == 0.83


def test_body_weight_zero_is_rejected():
    with pytest.raises(
        ExposureValidationError,
        match=(
            "body_weight must be greater than zero"
        ),
    ):
        validate_exposure_data(
            body_weight=0,
            exposure_time=8,
            exposure_frequency=250,
            exposure_duration=10,
            inhalation_rate=0.83,
        )


def test_zero_exposure_time_is_rejected():
    with pytest.raises(
        ExposureValidationError,
        match=(
            "exposure_time must be greater than zero"
        ),
    ):
        validate_exposure_data(
            body_weight=55,
            exposure_time=0,
            exposure_frequency=250,
            exposure_duration=10,
            inhalation_rate=0.83,
        )


def test_negative_exposure_time_is_rejected():
    with pytest.raises(
        ExposureValidationError,
        match=(
            "exposure_time must be greater than zero"
        ),
    ):
        validate_exposure_data(
            body_weight=55,
            exposure_time=-1,
            exposure_frequency=250,
            exposure_duration=10,
            inhalation_rate=0.83,
        )


def test_exposure_time_above_24_is_rejected():
    with pytest.raises(
        ExposureValidationError,
        match=(
            "exposure_time cannot exceed "
            "24 hours/day"
        ),
    ):
        validate_exposure_data(
            body_weight=55,
            exposure_time=25,
            exposure_frequency=250,
            exposure_duration=10,
            inhalation_rate=0.83,
        )


def test_zero_exposure_frequency_is_rejected():
    with pytest.raises(
        ExposureValidationError,
        match=(
            "exposure_frequency must be "
            "greater than zero"
        ),
    ):
        validate_exposure_data(
            body_weight=55,
            exposure_time=8,
            exposure_frequency=0,
            exposure_duration=10,
            inhalation_rate=0.83,
        )


def test_exposure_frequency_above_365_is_rejected():
    with pytest.raises(
        ExposureValidationError,
        match=(
            "exposure_frequency cannot exceed "
            "365 days/year"
        ),
    ):
        validate_exposure_data(
            body_weight=55,
            exposure_time=8,
            exposure_frequency=366,
            exposure_duration=10,
            inhalation_rate=0.83,
        )


def test_zero_exposure_duration_is_rejected():
    with pytest.raises(
        ExposureValidationError,
        match=(
            "exposure_duration must be "
            "greater than zero"
        ),
    ):
        validate_exposure_data(
            body_weight=55,
            exposure_time=8,
            exposure_frequency=250,
            exposure_duration=0,
            inhalation_rate=0.83,
        )


def test_zero_inhalation_rate_is_rejected():
    with pytest.raises(
        ExposureValidationError,
        match=(
            "inhalation_rate must be "
            "greater than zero"
        ),
    ):
        validate_exposure_data(
            body_weight=55,
            exposure_time=8,
            exposure_frequency=250,
            exposure_duration=10,
            inhalation_rate=0,
        )


def test_non_numeric_exposure_value_is_rejected():
    with pytest.raises(
        ExposureValidationError,
        match="body_weight must be numeric",
    ):
        validate_exposure_data(
            body_weight="55",
            exposure_time=8,
            exposure_frequency=250,
            exposure_duration=10,
            inhalation_rate=0.83,
        )


# ============================================================
# WORKER API
# ============================================================


@pytest.mark.django_db
def test_worker_can_be_created_via_api(
    client,
):
    response = client.post(
        "/api/v1/workers/",
        data={
            "code": "PML-API-001",
            "name": "Ahmad",
            "age": 40,
        },
        content_type="application/json",
    )

    assert response.status_code == 201

    worker = Worker.objects.get(
        code="PML-API-001"
    )

    assert worker.name == "Ahmad"
    assert worker.age == 40
    assert worker.is_active is True


@pytest.mark.django_db
def test_worker_api_requires_name(
    client,
):
    response = client.post(
        "/api/v1/workers/",
        data={
            "code": "PML-NO-NAME",
            "age": 35,
        },
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_worker_api_requires_age(
    client,
):
    response = client.post(
        "/api/v1/workers/",
        data={
            "code": "PML-NO-AGE",
            "name": "Ahmad",
        },
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_worker_api_rejects_blank_name(
    client,
):
    response = client.post(
        "/api/v1/workers/",
        data={
            "code": "PML-BLANK-NAME",
            "name": "   ",
            "age": 35,
        },
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_worker_api_rejects_invalid_age(
    client,
):
    response = client.post(
        "/api/v1/workers/",
        data={
            "code": "PML-AGE-INVALID",
            "name": "Ahmad",
            "age": 0,
        },
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_worker_api_returns_identity(
    client,
):
    worker = Worker.objects.create(
        code="PML-DETAIL-001",
        name="Sudirman",
        age=45,
    )

    response = client.get(
        f"/api/v1/workers/{worker.pk}/"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["code"] == "PML-DETAIL-001"
    assert data["name"] == "Sudirman"
    assert data["age"] == 45


# ============================================================
# EXPOSURE PROFILE API
# ============================================================


@pytest.mark.django_db
def test_exposure_profile_can_be_created_via_api(
    client,
):
    worker = Worker.objects.create(
        code="PML-001",
        name="Ahmad",
        age=40,
    )

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

    data = response.json()

    assert data["worker"] == worker.pk
    assert data["worker_code"] == "PML-001"
    assert data["worker_name"] == "Ahmad"


@pytest.mark.django_db
def test_exposure_profile_can_be_patched(
    client,
):
    worker = Worker.objects.create(
        code="PML-001",
        name="Ahmad",
        age=40,
    )

    profile = ExposureProfile.objects.create(
        worker=worker,
        body_weight=55,
        exposure_time=8,
        exposure_frequency=250,
        exposure_duration=10,
        inhalation_rate=0.83,
    )

    response = client.patch(
        (
            "/api/v1/exposure-profiles/"
            f"{profile.pk}/"
        ),
        data={
            "body_weight": 60,
        },
        content_type="application/json",
    )

    assert response.status_code == 200

    profile.refresh_from_db()

    assert profile.body_weight == 60


@pytest.mark.django_db
def test_invalid_exposure_returns_400(
    client,
):
    worker = Worker.objects.create(
        code="PML-001",
        name="Ahmad",
        age=40,
    )

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


@pytest.mark.django_db
def test_exposure_api_rejects_time_above_24(
    client,
):
    worker = Worker.objects.create(
        code="PML-TIME-API",
        name="Ahmad",
        age=40,
    )

    response = client.post(
        "/api/v1/exposure-profiles/",
        data={
            "worker": worker.pk,
            "body_weight": 55,
            "exposure_time": 25,
            "exposure_frequency": 250,
            "exposure_duration": 10,
            "inhalation_rate": 0.83,
        },
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_exposure_api_rejects_frequency_above_365(
    client,
):
    worker = Worker.objects.create(
        code="PML-FREQ-API",
        name="Ahmad",
        age=40,
    )

    response = client.post(
        "/api/v1/exposure-profiles/",
        data={
            "worker": worker.pk,
            "body_weight": 55,
            "exposure_time": 8,
            "exposure_frequency": 366,
            "exposure_duration": 10,
            "inhalation_rate": 0.83,
        },
        content_type="application/json",
    )

    assert response.status_code == 400

@pytest.fixture
def operator_api_client():
    user = User.objects.create_user(
        username="exposure-operator",
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

@pytest.mark.django_db
def test_worker_can_be_created_via_api(
    operator_api_client,
):
    response = operator_api_client.post(
        "/api/v1/workers/",
        {
            "code": "PML-API-001",
            "name": "Ahmad",
            "age": 40,
        },
        format="json",
    )

    assert response.status_code == 201

    worker = Worker.objects.get(
        code="PML-API-001"
    )

    assert worker.name == "Ahmad"
    assert worker.age == 40

@pytest.mark.django_db
def test_worker_api_requires_name(
    operator_api_client,
):
    response = operator_api_client.post(
        "/api/v1/workers/",
        {
            "code": "PML-NO-NAME",
            "age": 35,
        },
        format="json",
    )

    assert response.status_code == 400

@pytest.mark.django_db
def test_worker_api_requires_age(
    operator_api_client,
):
    response = operator_api_client.post(
        "/api/v1/workers/",
        {
            "code": "PML-NO-AGE",
            "name": "Ahmad",
        },
        format="json",
    )

    assert response.status_code == 400

@pytest.mark.django_db
def test_worker_api_rejects_blank_name(
    operator_api_client,
):
    response = operator_api_client.post(
        "/api/v1/workers/",
        {
            "code": "PML-BLANK-NAME",
            "name": "   ",
            "age": 35,
        },
        format="json",
    )

    assert response.status_code == 400

@pytest.mark.django_db
def test_worker_api_rejects_invalid_age(
    operator_api_client,
):
    response = operator_api_client.post(
        "/api/v1/workers/",
        {
            "code": "PML-AGE-INVALID",
            "name": "Ahmad",
            "age": 0,
        },
        format="json",
    )

    assert response.status_code == 400

@pytest.mark.django_db
def test_worker_api_returns_identity(
    operator_api_client,
):
    worker = Worker.objects.create(
        code="PML-DETAIL-001",
        name="Sudirman",
        age=45,
    )

    response = operator_api_client.get(
        f"/api/v1/workers/{worker.pk}/"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["code"] == "PML-DETAIL-001"
    assert data["name"] == "Sudirman"
    assert data["age"] == 45

@pytest.mark.django_db
def test_exposure_profile_can_be_created_via_api(
    operator_api_client,
):
    worker = Worker.objects.create(
        code="PML-001",
        name="Ahmad",
        age=40,
    )

    response = operator_api_client.post(
        "/api/v1/exposure-profiles/",
        {
            "worker": worker.pk,
            "body_weight": 55,
            "exposure_time": 8,
            "exposure_frequency": 250,
            "exposure_duration": 10,
            "inhalation_rate": 0.83,
        },
        format="json",
    )

    assert response.status_code == 201
    assert ExposureProfile.objects.count() == 1

    data = response.json()

    assert data["worker"] == worker.pk
    assert data["worker_code"] == "PML-001"
    assert data["worker_name"] == "Ahmad"

@pytest.mark.django_db
def test_exposure_profile_can_be_patched(
    operator_api_client,
):
    worker = Worker.objects.create(
        code="PML-001",
        name="Ahmad",
        age=40,
    )

    profile = ExposureProfile.objects.create(
        worker=worker,
        body_weight=55,
        exposure_time=8,
        exposure_frequency=250,
        exposure_duration=10,
        inhalation_rate=0.83,
    )

    response = operator_api_client.patch(
        (
            "/api/v1/exposure-profiles/"
            f"{profile.pk}/"
        ),
        {
            "body_weight": 60,
        },
        format="json",
    )

    assert response.status_code == 200

    profile.refresh_from_db()

    assert profile.body_weight == 60

@pytest.mark.django_db
def test_invalid_exposure_returns_400(
    operator_api_client,
):
    worker = Worker.objects.create(
        code="PML-001",
        name="Ahmad",
        age=40,
    )

    response = operator_api_client.post(
        "/api/v1/exposure-profiles/",
        {
            "worker": worker.pk,
            "body_weight": -1,
            "exposure_time": 8,
            "exposure_frequency": 250,
            "exposure_duration": 10,
            "inhalation_rate": 0.83,
        },
        format="json",
    )

    assert response.status_code == 400

@pytest.mark.django_db
def test_exposure_api_rejects_time_above_24(
    operator_api_client,
):
    worker = Worker.objects.create(
        code="PML-TIME-API",
        name="Ahmad",
        age=40,
    )

    response = operator_api_client.post(
        "/api/v1/exposure-profiles/",
        {
            "worker": worker.pk,
            "body_weight": 55,
            "exposure_time": 25,
            "exposure_frequency": 250,
            "exposure_duration": 10,
            "inhalation_rate": 0.83,
        },
        format="json",
    )

    assert response.status_code == 400

@pytest.mark.django_db
def test_exposure_api_rejects_frequency_above_365(
    operator_api_client,
):
    worker = Worker.objects.create(
        code="PML-FREQ-API",
        name="Ahmad",
        age=40,
    )

    response = operator_api_client.post(
        "/api/v1/exposure-profiles/",
        {
            "worker": worker.pk,
            "body_weight": 55,
            "exposure_time": 8,
            "exposure_frequency": 366,
            "exposure_duration": 10,
            "inhalation_rate": 0.83,
        },
        format="json",
    )

    assert response.status_code == 400

@pytest.mark.django_db
def test_anonymous_cannot_access_workers_api(
    client,
):
    response = client.get(
        "/api/v1/workers/"
    )

    assert response.status_code == 401

@pytest.mark.django_db
def test_worker_role_cannot_access_workers_admin_api():
    worker = Worker.objects.create(
        code="PML-WORKER-ROLE",
        name="Worker Role",
        age=40,
    )

    user = User.objects.create_user(
        username="exposure-worker",
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

    response = client.get(
        "/api/v1/workers/"
    )

    assert response.status_code == 403

@pytest.mark.django_db
def test_researcher_cannot_access_workers_admin_api():
    user = User.objects.create_user(
        username="exposure-researcher",
        password="StrongPass123!",
    )

    AccountProfile.objects.create(
        user=user,
        role=AccountProfile.Role.RESEARCHER,
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

    response = client.get(
        "/api/v1/workers/"
    )

    assert response.status_code == 403    