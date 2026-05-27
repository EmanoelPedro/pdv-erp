from fastapi.testclient import TestClient


def _open_cash_register(client: TestClient, headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/cash-register/open",
        json={"opening_amount": "200.00"},
        headers=headers,
    )
    return response.json()["id"]


def test_owner_can_crud_expenses(
    client: TestClient,
    owner_auth_headers: dict[str, str],
) -> None:
    session_id = _open_cash_register(client, owner_auth_headers)

    create_response = client.post(
        "/api/v1/expenses",
        json={
            "description": "Compra de gas",
            "amount": "80.00",
            "category": "UTILITIES",
            "payment_method": "CASH",
            "cash_register_session_id": session_id,
            "notes": "Botijao",
        },
        headers=owner_auth_headers,
    )

    assert create_response.status_code == 201
    expense_id = create_response.json()["id"]

    list_response = client.get(
        f"/api/v1/expenses?category=UTILITIES&cash_register_session_id={session_id}",
        headers=owner_auth_headers,
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = client.get(
        f"/api/v1/expenses/{expense_id}",
        headers=owner_auth_headers,
    )
    assert get_response.status_code == 200
    assert get_response.json()["description"] == "Compra de gas"

    update_response = client.put(
        f"/api/v1/expenses/{expense_id}",
        json={
            "description": "Compra de gas atualizada",
            "amount": "75.00",
            "category": "UTILITIES",
            "payment_method": "PIX",
            "cash_register_session_id": session_id,
            "notes": "Pagamento no app",
        },
        headers=owner_auth_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["amount"] == "75.00"
    assert update_response.json()["payment_method"] == "PIX"

    delete_response = client.delete(
        f"/api/v1/expenses/{expense_id}",
        headers=owner_auth_headers,
    )
    assert delete_response.status_code == 204


def test_employee_cannot_access_expenses(
    client: TestClient,
    owner_auth_headers: dict[str, str],
    employee_auth_headers: dict[str, str],
) -> None:
    session_id = _open_cash_register(client, owner_auth_headers)

    create_response = client.post(
        "/api/v1/expenses",
        json={
            "description": "Compra",
            "amount": "20.00",
            "category": "OTHER",
            "payment_method": "CASH",
            "cash_register_session_id": session_id,
        },
        headers=employee_auth_headers,
    )
    list_response = client.get(
        "/api/v1/expenses",
        headers=employee_auth_headers,
    )

    assert create_response.status_code == 403
    assert list_response.status_code == 403


def test_closed_session_expense_is_immutable_via_api(
    client: TestClient,
    owner_auth_headers: dict[str, str],
) -> None:
    session_id = _open_cash_register(client, owner_auth_headers)
    create_response = client.post(
        "/api/v1/expenses",
        json={
            "description": "Retirada",
            "amount": "30.00",
            "category": "WITHDRAWAL",
            "payment_method": "CASH",
            "cash_register_session_id": session_id,
        },
        headers=owner_auth_headers,
    )
    expense_id = create_response.json()["id"]

    close_response = client.post(
        f"/api/v1/cash-register/{session_id}/close",
        json={"closing_amount": "170.00", "owner_pin": "1234"},
        headers=owner_auth_headers,
    )
    assert close_response.status_code == 200

    update_response = client.put(
        f"/api/v1/expenses/{expense_id}",
        json={
            "description": "Retirada ajustada",
            "amount": "35.00",
            "category": "WITHDRAWAL",
            "payment_method": "CASH",
            "cash_register_session_id": session_id,
        },
        headers=owner_auth_headers,
    )

    assert update_response.status_code == 409
    assert update_response.json()[
        "detail"] == "Expenses linked to a closed cash register session cannot be changed."
