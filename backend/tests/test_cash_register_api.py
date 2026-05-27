from uuid import uuid4

from fastapi.testclient import TestClient


def test_open_cash_register_endpoint(
    client: TestClient,
    owner_auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/cash-register/open",
        json={"opening_amount": "125.00"},
        headers=owner_auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["status"] == "OPEN"
    assert response.json()["opening_amount"] == "125.00"
    assert response.json()["totals"]["expected_amount"] == "125.00"


def test_current_cash_register_endpoint(
    client: TestClient,
    owner_auth_headers: dict[str, str],
) -> None:
    client.post(
        "/api/v1/cash-register/open",
        json={"opening_amount": "90.00"},
        headers=owner_auth_headers,
    )

    response = client.get("/api/v1/cash-register/current",
                          headers=owner_auth_headers)

    assert response.status_code == 200
    assert response.json()["status"] == "OPEN"
    assert response.json()["opening_amount"] == "90.00"


def test_close_cash_register_endpoint(
    client: TestClient,
    owner_auth_headers: dict[str, str],
) -> None:
    open_response = client.post(
        "/api/v1/cash-register/open",
        json={"opening_amount": "110.00"},
        headers=owner_auth_headers,
    )
    session_id = open_response.json()["id"]

    response = client.post(
        f"/api/v1/cash-register/{session_id}/close",
        json={"closing_amount": "105.50", "owner_pin": "1234"},
        headers=owner_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "CLOSED"
    assert response.json()["closing_amount"] == "105.50"
    assert response.json()["difference_amount"] == "-4.50"


def test_validation_errors_on_open_and_close(
    client: TestClient,
    owner_auth_headers: dict[str, str],
) -> None:
    invalid_open_response = client.post(
        "/api/v1/cash-register/open",
        json={"opening_amount": "-1.00"},
        headers=owner_auth_headers,
    )

    invalid_close_response = client.post(
        f"/api/v1/cash-register/{uuid4()}/close",
        json={"closing_amount": "10.00", "owner_pin": "1234"},
        headers=owner_auth_headers,
    )

    assert invalid_open_response.status_code == 422
    assert invalid_close_response.status_code == 404


def test_close_endpoint_requires_owner_role(
    client: TestClient,
    owner_auth_headers: dict[str, str],
    employee_auth_headers: dict[str, str],
) -> None:
    open_response = client.post(
        "/api/v1/cash-register/open",
        json={"opening_amount": "40.00"},
        headers=owner_auth_headers,
    )
    session_id = open_response.json()["id"]

    response = client.post(
        f"/api/v1/cash-register/{session_id}/close",
        json={"closing_amount": "40.00", "owner_pin": "5678"},
        headers=employee_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()[
        "detail"] == "Owner approval is required for this action."


def test_cash_register_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/cash-register/current")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication is required."


def test_close_endpoint_requires_valid_owner_pin(
    client: TestClient,
    owner_auth_headers: dict[str, str],
) -> None:
    open_response = client.post(
        "/api/v1/cash-register/open",
        json={"opening_amount": "40.00"},
        headers=owner_auth_headers,
    )
    session_id = open_response.json()["id"]

    response = client.post(
        f"/api/v1/cash-register/{session_id}/close",
        json={"closing_amount": "40.00", "owner_pin": "0000"},
        headers=owner_auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid owner PIN."


def test_cash_register_history_returns_session_summaries(
    client: TestClient,
    owner_auth_headers: dict[str, str],
) -> None:
    open_response = client.post(
        "/api/v1/cash-register/open",
        json={"opening_amount": "90.00"},
        headers=owner_auth_headers,
    )
    session_id = open_response.json()["id"]
    client.post(
        f"/api/v1/cash-register/{session_id}/close",
        json={"closing_amount": "90.00", "owner_pin": "1234"},
        headers=owner_auth_headers,
    )

    history_response = client.get(
        "/api/v1/cash-register/history",
        headers=owner_auth_headers,
    )
    detail_response = client.get(
        f"/api/v1/cash-register/{session_id}",
        headers=owner_auth_headers,
    )

    assert history_response.status_code == 200
    assert history_response.json()[0]["id"] == session_id
    assert detail_response.status_code == 200
    assert detail_response.json()["totals"]["expenses_amount"] == "0.00"
