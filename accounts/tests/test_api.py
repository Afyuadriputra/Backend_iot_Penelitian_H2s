import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.models import AccountProfile
from exposure.models import Worker


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_login_returns_token(
    api_client,
    operator_user,
):
    response = api_client.post(
        "/api/v1/auth/login/",
        {
            "username": "operator-test",
            "password": "StrongPass123!",
        },
        format="json",
    )

    assert response.status_code == 200

    data = response.json()

    assert "token" in data

    assert (
        data["user"]["role"]
        == AccountProfile.Role.OPERATOR
    )


@pytest.mark.django_db
def test_invalid_login_returns_400(
    api_client,
):
    response = api_client.post(
        "/api/v1/auth/login/",
        {
            "username": "unknown",
            "password": "wrong-password",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_me_requires_authentication(
    api_client,
):
    response = api_client.get(
        "/api/v1/auth/me/"
    )

    assert response.status_code in (
        401,
        403,
    )


@pytest.mark.django_db
def test_worker_me_returns_worker_identity(
    api_client,
    worker_user,
):
    token = Token.objects.create(
        user=worker_user
    )

    api_client.credentials(
        HTTP_AUTHORIZATION=(
            f"Token {token.key}"
        )
    )

    response = api_client.get(
        "/api/v1/auth/me/"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["role"]
        == AccountProfile.Role.WORKER
    )

    assert (
        data["worker_code"]
        == "PML-AUTH-001"
    )

    assert (
        data["worker_name"]
        == "Worker Test"
    )


@pytest.mark.django_db
def test_admin_can_create_operator(
    api_client,
    admin_user,
):
    token = Token.objects.create(
        user=admin_user
    )

    api_client.credentials(
        HTTP_AUTHORIZATION=(
            f"Token {token.key}"
        )
    )

    response = api_client.post(
        "/api/v1/accounts/",
        {
            "username": "new-operator",
            "password": "StrongPass123!",
            "role": "OPERATOR",
        },
        format="json",
    )

    assert response.status_code == 201

    assert (
        response.json()["role"]
        == "OPERATOR"
    )


@pytest.mark.django_db
def test_operator_cannot_create_account(
    api_client,
    operator_user,
):
    token = Token.objects.create(
        user=operator_user
    )

    api_client.credentials(
        HTTP_AUTHORIZATION=(
            f"Token {token.key}"
        )
    )

    response = api_client.post(
        "/api/v1/accounts/",
        {
            "username": "forbidden-user",
            "password": "StrongPass123!",
            "role": "RESEARCHER",
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_can_create_worker_account(
    api_client,
    admin_user,
):
    worker = Worker.objects.create(
        code="PML-API-WORKER",
        name="Ahmad",
        age=42,
    )

    token = Token.objects.create(
        user=admin_user
    )

    api_client.credentials(
        HTTP_AUTHORIZATION=(
            f"Token {token.key}"
        )
    )

    response = api_client.post(
        "/api/v1/accounts/",
        {
            "username": "worker-api",
            "password": "StrongPass123!",
            "role": "WORKER",
            "worker_id": worker.id,
        },
        format="json",
    )

    assert response.status_code == 201

    data = response.json()

    assert data["role"] == "WORKER"
    assert data["worker"] == worker.id
    assert data["worker_code"] == (
        "PML-API-WORKER"
    )


@pytest.mark.django_db
def test_logout_deletes_token(
    api_client,
    operator_user,
):
    token = Token.objects.create(
        user=operator_user
    )

    api_client.credentials(
        HTTP_AUTHORIZATION=(
            f"Token {token.key}"
        )
    )

    response = api_client.post(
        "/api/v1/auth/logout/"
    )

    assert response.status_code == 204

    assert not Token.objects.filter(
        user=operator_user
    ).exists()