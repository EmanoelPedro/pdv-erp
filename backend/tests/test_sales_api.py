from fastapi.testclient import TestClient


def test_cash_sale_updates_expected_amount(
    client: TestClient,
    owner_auth_headers: dict[str, str],
) -> None:
    category_response = client.post(
        "/api/v1/catalog/categories",
        json={"name": "Pastel"},
        headers=owner_auth_headers,
    )
    category_id = category_response.json()["id"]

    product_response = client.post(
        "/api/v1/catalog/products",
        json={
            "category_id": category_id,
            "name": "Pastel de Carne",
            "price": "12.00",
        },
        headers=owner_auth_headers,
    )
    product_id = product_response.json()["id"]

    client.post(
        "/api/v1/cash-register/open",
        json={"opening_amount": "20.00"},
        headers=owner_auth_headers,
    )

    sale_response = client.post(
        "/api/v1/sales",
        json={
            "items": [{"product_id": product_id, "quantity": 2}],
            "payment_method": "CASH",
        },
        headers=owner_auth_headers,
    )

    assert sale_response.status_code == 201
    assert sale_response.json()["sale"]["total_amount"] == "24.00"
    assert sale_response.json(
    )["cash_register_session"]["expected_amount"] == "44.00"


def test_sale_requires_open_cash_register(
    client: TestClient,
    owner_auth_headers: dict[str, str],
) -> None:
    category_response = client.post(
        "/api/v1/catalog/categories",
        json={"name": "Bebidas"},
        headers=owner_auth_headers,
    )
    product_response = client.post(
        "/api/v1/catalog/products",
        json={
            "category_id": category_response.json()["id"],
            "name": "Caldo 300",
            "price": "8.50",
        },
        headers=owner_auth_headers,
    )

    sale_response = client.post(
        "/api/v1/sales",
        json={
            "items": [{"product_id": product_response.json()["id"], "quantity": 1}],
            "payment_method": "PIX",
        },
        headers=owner_auth_headers,
    )

    assert sale_response.status_code == 409
    assert sale_response.json(
    )["detail"] == "An open cash register is required to make a sale."


def test_mixed_payment_only_updates_cash_component(
    client: TestClient,
    owner_auth_headers: dict[str, str],
) -> None:
    category_response = client.post(
        "/api/v1/catalog/categories",
        json={"name": "Lanches"},
        headers=owner_auth_headers,
    )
    product_response = client.post(
        "/api/v1/catalog/products",
        json={
            "category_id": category_response.json()["id"],
            "name": "Hamburguer",
            "price": "30.00",
        },
        headers=owner_auth_headers,
    )

    client.post(
        "/api/v1/cash-register/open",
        json={"opening_amount": "50.00"},
        headers=owner_auth_headers,
    )

    sale_response = client.post(
        "/api/v1/sales",
        json={
            "items": [{"product_id": product_response.json()["id"], "quantity": 1}],
            "payment_method": "MIXED",
            "cash_amount": "10.00",
            "pix_amount": "20.00",
        },
        headers=owner_auth_headers,
    )

    assert sale_response.status_code == 201
    assert sale_response.json(
    )["cash_register_session"]["expected_amount"] == "60.00"
    assert sale_response.json()["sale"]["cash_amount"] == "10.00"


def test_cash_register_expected_amount_subtracts_only_cash_expenses(
    client: TestClient,
    owner_auth_headers: dict[str, str],
) -> None:
    category_response = client.post(
        "/api/v1/catalog/categories",
        json={"name": "Porcoes"},
        headers=owner_auth_headers,
    )
    product_response = client.post(
        "/api/v1/catalog/products",
        json={
            "category_id": category_response.json()["id"],
            "name": "Batata",
            "price": "50.00",
        },
        headers=owner_auth_headers,
    )
    product_id = product_response.json()["id"]

    open_response = client.post(
        "/api/v1/cash-register/open",
        json={"opening_amount": "300.00"},
        headers=owner_auth_headers,
    )
    session_id = open_response.json()["id"]

    client.post(
        "/api/v1/sales",
        json={
            "items": [{"product_id": product_id, "quantity": 14}],
            "payment_method": "CASH",
        },
        headers=owner_auth_headers,
    )
    client.post(
        "/api/v1/sales",
        json={
            "items": [{"product_id": product_id, "quantity": 8}],
            "payment_method": "PIX",
        },
        headers=owner_auth_headers,
    )
    client.post(
        "/api/v1/sales",
        json={
            "items": [{"product_id": product_id, "quantity": 4}],
            "payment_method": "DEBIT_CARD",
        },
        headers=owner_auth_headers,
    )
    expense_response = client.post(
        "/api/v1/expenses",
        json={
            "description": "Compra de farinha",
            "amount": "150.00",
            "category": "INGREDIENTS",
            "payment_method": "CASH",
            "cash_register_session_id": session_id,
        },
        headers=owner_auth_headers,
    )
    assert expense_response.status_code == 201

    current_response = client.get(
        "/api/v1/cash-register/current",
        headers=owner_auth_headers,
    )
    close_response = client.post(
        f"/api/v1/cash-register/{session_id}/close",
        json={"closing_amount": "850.00", "owner_pin": "1234"},
        headers=owner_auth_headers,
    )

    assert current_response.status_code == 200
    assert current_response.json()["totals"]["cash_sales_amount"] == "700.00"
    assert current_response.json()["totals"]["pix_sales_amount"] == "400.00"
    assert current_response.json(
    )["totals"]["debit_card_sales_amount"] == "200.00"
    assert current_response.json(
    )["totals"]["cash_expenses_amount"] == "150.00"
    assert current_response.json()["expected_amount"] == "850.00"
    assert close_response.status_code == 200
    assert close_response.json()["difference_amount"] == "0.00"
