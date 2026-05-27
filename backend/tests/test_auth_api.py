from fastapi.testclient import TestClient


def test_bootstrap_owner_registration_and_login(client: TestClient) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Dona Loja",
            "username": "owner",
            "pin": "1234",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "owner", "pin": "1234"},
    )

    assert register_response.status_code == 201
    assert register_response.json()["role"] == "OWNER"
    assert login_response.status_code == 200
    assert login_response.json()["user"]["username"] == "owner"
    assert login_response.json()["access_token"]


def test_owner_can_create_employee(
    client: TestClient,
    owner_auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Atendente",
            "username": "employee",
            "pin": "5678",
            "role": "EMPLOYEE",
        },
        headers=owner_auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["role"] == "EMPLOYEE"
