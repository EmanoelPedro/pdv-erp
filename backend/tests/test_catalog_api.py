from io import BytesIO

from fastapi.testclient import TestClient


def test_owner_can_upload_product_image(
    client: TestClient,
    owner_auth_headers: dict[str, str],
) -> None:
    category_response = client.post(
        "/api/v1/catalog/categories",
        json={"name": "Pasteis"},
        headers=owner_auth_headers,
    )

    product_response = client.post(
        "/api/v1/catalog/products",
        json={
            "category_id": category_response.json()["id"],
            "name": "Pastel de Carne",
            "price": "10.00",
            "emoji": "🥟",
        },
        headers=owner_auth_headers,
    )

    upload_response = client.post(
        f"/api/v1/catalog/products/{product_response.json()['id']}/image",
        files={"image": ("pastel.png", BytesIO(
            b"fake image bytes"), "image/png")},
        headers=owner_auth_headers,
    )

    assert upload_response.status_code == 200
    assert upload_response.json()["emoji"] == "🥟"
    assert upload_response.json()["image_path"].startswith("/media/products/")


def test_upload_rejects_invalid_product_image(
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
            "name": "Caldo de Cana",
            "price": "5.00",
        },
        headers=owner_auth_headers,
    )

    upload_response = client.post(
        f"/api/v1/catalog/products/{product_response.json()['id']}/image",
        files={"image": ("produto.txt", BytesIO(
            b"not an image"), "text/plain")},
        headers=owner_auth_headers,
    )

    assert upload_response.status_code == 422
    assert upload_response.json(
    )["detail"] == "Use uma imagem JPG, PNG, WEBP ou GIF para o produto."


def test_owner_can_update_product_and_remove_image(
    client: TestClient,
    owner_auth_headers: dict[str, str],
) -> None:
    category_response = client.post(
        "/api/v1/catalog/categories",
        json={"name": "Salgados"},
        headers=owner_auth_headers,
    )
    category_id = category_response.json()["id"]

    product_response = client.post(
        "/api/v1/catalog/products",
        json={
            "category_id": category_id,
            "name": "Coxinha",
            "price": "5.00",
            "emoji": "🧆",
        },
        headers=owner_auth_headers,
    )
    product_id = product_response.json()["id"]

    client.post(
        f"/api/v1/catalog/products/{product_id}/image",
        files={"image": ("pastel.png", BytesIO(
            b"fake image bytes"), "image/png")},
        headers=owner_auth_headers,
    )

    update_response = client.put(
        f"/api/v1/catalog/products/{product_id}",
        json={
            "category_id": category_id,
            "name": "Coxinha Especial",
            "price": "7.50",
            "emoji": "🔥",
            "remove_image": True,
        },
        headers=owner_auth_headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Coxinha Especial"
    assert update_response.json()["price"] == "7.50"
    assert update_response.json()["emoji"] == "🔥"
    assert update_response.json()["image_path"] is None


def test_owner_can_deactivate_and_restore_product(
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
            "name": "X-Bacon",
            "price": "24.00",
        },
        headers=owner_auth_headers,
    )
    product_id = product_response.json()["id"]

    deactivate_response = client.post(
        f"/api/v1/catalog/products/{product_id}/deactivate",
        headers=owner_auth_headers,
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    list_active_response = client.get(
        "/api/v1/catalog/products",
        headers=owner_auth_headers,
    )
    assert all(product["id"] !=
               product_id for product in list_active_response.json())

    list_all_response = client.get(
        "/api/v1/catalog/products?include_inactive=true",
        headers=owner_auth_headers,
    )
    assert any(product["id"] ==
               product_id for product in list_all_response.json())

    restore_response = client.post(
        f"/api/v1/catalog/products/{product_id}/restore",
        headers=owner_auth_headers,
    )
    assert restore_response.status_code == 200
    assert restore_response.json()["is_active"] is True
