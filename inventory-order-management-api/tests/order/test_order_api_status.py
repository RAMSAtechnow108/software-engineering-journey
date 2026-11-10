
import uuid

from app.constants.user_constants import UserRole
from app.repositories.user_repository import UserRepository
from app.security.password import hash_password
from app.repositories.inventory_repository import InventoryRepository


def _register_customer(client):
    suffix = uuid.uuid4().hex[:10]
    email = f"status-api-{suffix}@example.com"
    phone = str(9_000_000_000 + uuid.uuid4().int % 999_999_999)
    password = "StrongPass123"

    response = client.post(
        "/users/register",
        json={
            "name": f"Status API Customer {suffix}",
            "email": email,
            "phone": phone,
            "password": password,
        },
    )
    assert response.status_code == 201, response.text

    login = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200, login.text

    return login.json()["access_token"]


def _admin_token(client, db):
    suffix = uuid.uuid4().hex[:10]
    email = f"status-admin-{suffix}@example.com"
    password = "AdminPass123"

    UserRepository(db).create_admin_user(
        email=email,
        password_hash=hash_password(password),
    )
    db.commit()

    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text

    return response.json()["access_token"]


def _admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


def _create_pending_order(client, customer_token, admin_token):
    suffix = uuid.uuid4().hex[:8]

    category_response = client.post(
        "/categories/",
        headers=_admin_headers(admin_token),
        json={"name": f"Status Category {suffix}"},
    )
    assert category_response.status_code == 201, category_response.text
    category_id = category_response.json()["id"]

    product_response = client.post(
        "/products/",
        headers=_admin_headers(admin_token),
        json={
            "name": f"Status Product {suffix}",
            "price": 500,
            "category_id": category_id,
            "inventory": {"total_quantity": 5},
        },
    )
    assert product_response.status_code == 201, product_response.text
    product_id = product_response.json()["id"]

    response = client.post(
        "/order/",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"items": [{"product_id": product_id, "quantity": 1}]},
    )
    assert response.status_code == 201, response.text

    return response.json()["id"], product_id


def test_status_update_requires_authentication(client):
    response = client.patch(
        "/order/2000000000/status",
        json={"status": "confirmed"},
    )

    assert response.status_code == 401


def test_status_update_rejects_invalid_status_payload(client):
    token = _register_customer(client)

    response = client.patch(
        "/order/2000000000/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "not-a-valid-status"},
    )

    assert response.status_code == 422


def test_status_update_returns_404_for_missing_order(client, db):
    token = _admin_token(client, db)

    response = client.patch(
        "/order/2000000000/status",
        headers=_admin_headers(token),
        json={"status": "confirmed"},
    )

    assert response.status_code == 404, response.text


def test_invalid_status_transition_returns_conflict(client, db):
    customer_token = _register_customer(client)
    admin_token = _admin_token(client, db)

    order_id, _ = _create_pending_order(
        client,
        customer_token,
        admin_token,
    )

    # A PENDING order cannot jump directly to SHIPPED.
    response = client.patch(
        f"/order/{order_id}/status",
        headers=_admin_headers(admin_token),
        json={"status": "shipped"},
    )

    assert response.status_code == 409, response.text
    assert response.json()["success"] is False
    assert (
        response.json()["error_code"]
        == "INVALID_ORDER_STATUS_TRANSITION"
    )


def test_shipping_deducts_total_and_reserved_inventory(client, db):
    customer_token = _register_customer(client)
    admin_token = _admin_token(client, db)

    order_id, product_id = _create_pending_order(
        client,
        customer_token,
        admin_token,
    )

    inventory_repository = InventoryRepository(db)

    inventory = inventory_repository.get_inventory_by_product_id(
        product_id
    )
    assert inventory.total_quantity == 5
    assert inventory.reserved_quantity == 1
    assert inventory.available_quantity == 4

    # Admin confirms the order.
    confirmed_response = client.patch(
        f"/order/{order_id}/status",
        headers=_admin_headers(admin_token),
        json={"status": "confirmed"},
    )
    assert confirmed_response.status_code == 200, confirmed_response.text

    # Admin ships the order.
    shipped_response = client.patch(
        f"/order/{order_id}/status",
        headers=_admin_headers(admin_token),
        json={"status": "shipped"},
    )
    assert shipped_response.status_code == 200, shipped_response.text
    assert shipped_response.json()["status"].lower() == "shipped"

    # Verify stock was deducted and the reservation was released.
    inventory = inventory_repository.get_inventory_by_product_id(
        product_id
    )

    assert inventory.total_quantity == 4
    assert inventory.reserved_quantity == 0
    assert inventory.available_quantity == 4
