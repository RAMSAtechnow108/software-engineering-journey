
import uuid

from app.constants.user_constants import UserRole
from app.repositories.user_repository import UserRepository
from app.repositories.inventory_repository import InventoryRepository
from app.security.password import hash_password


PASSWORD = "StrongPass123"


def unique_suffix():
    return uuid.uuid4().hex[:10]


def register_customer_and_get_token(client):
    suffix = unique_suffix()
    email = f"auth-customer-{suffix}@example.com"
    phone = str(9_000_000_000 + uuid.uuid4().int % 999_999_999)

    registration = client.post(
        "/users/register",
        json={
            "name": f"Auth Customer {suffix}",
            "email": email,
            "phone": phone,
            "password": PASSWORD,
        },
    )
    assert registration.status_code == 201, registration.text

    login = client.post(
        "/auth/login",
        json={"email": email, "password": PASSWORD},
    )
    assert login.status_code == 200, login.text

    return login.json()["access_token"]


def create_admin_and_get_token(client, db):
    email = f"auth-admin-{unique_suffix()}@example.com"
    password = "AdminPass123"

    UserRepository(db).create_admin_user(
        email=email,
        password_hash=hash_password(password),
    )
    db.commit()

    login = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200, login.text

    return login.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_product_with_inventory(client, admin_token):
    suffix = unique_suffix()

    category_response = client.post(
        "/categories/",
        headers=auth_headers(admin_token),
        json={"name": f"Authorization Category {suffix}"},
    )
    assert category_response.status_code == 201, category_response.text
    category_id = category_response.json()["id"]

    product_response = client.post(
        "/products/",
        headers=auth_headers(admin_token),
        json={
            "name": f"Authorization Product {suffix}",
            "price": 500,
            "category_id": category_id,
            "inventory": {"total_quantity": 20},
        },
    )
    assert product_response.status_code == 201, product_response.text

    return product_response.json()["id"]


def create_order(client, customer_token, product_id, quantity=1):
    response = client.post(
        "/order/",
        headers=auth_headers(customer_token),
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": quantity,
                }
            ]
        },
    )
    assert response.status_code == 201, response.text

    return response.json()["id"]


def test_customer_cannot_update_order_status(client, db):
    admin_token = create_admin_and_get_token(client, db)
    customer_token = register_customer_and_get_token(client)

    product_id = create_product_with_inventory(client, admin_token)
    order_id = create_order(client, customer_token, product_id)

    response = client.patch(
        f"/order/{order_id}/status",
        headers=auth_headers(customer_token),
        json={"status": "confirmed"},
    )

    assert response.status_code == 403, response.text
    assert response.json()["detail"] == (
        "Only admin can update order status"
    )


def test_admin_can_update_order_status(client, db):
    admin_token = create_admin_and_get_token(client, db)
    customer_token = register_customer_and_get_token(client)

    product_id = create_product_with_inventory(client, admin_token)
    order_id = create_order(client, customer_token, product_id)

    response = client.patch(
        f"/order/{order_id}/status",
        headers=auth_headers(admin_token),
        json={"status": "confirmed"},
    )

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["id"] == order_id
    assert data["status"].lower() == "confirmed"


def test_customer_cannot_cancel_another_customers_order(client, db):
    admin_token = create_admin_and_get_token(client, db)

    customer_a_token = register_customer_and_get_token(client)
    customer_b_token = register_customer_and_get_token(client)

    product_id = create_product_with_inventory(client, admin_token)
    order_id = create_order(client, customer_b_token, product_id)

    response = client.patch(
        f"/order/{order_id}/cancel",
        headers=auth_headers(customer_a_token),
    )

    assert response.status_code == 403, response.text


def test_customer_can_cancel_own_order(client, db):
    admin_token = create_admin_and_get_token(client, db)
    customer_token = register_customer_and_get_token(client)

    product_id = create_product_with_inventory(client, admin_token)
    order_id = create_order(client, customer_token, product_id)

    inventory_repository = InventoryRepository(db)
    inventory_before = (
        inventory_repository.get_inventory_by_product_id(product_id)
    )

    reserved_before = inventory_before.reserved_quantity
    total_before = inventory_before.total_quantity

    response = client.patch(
        f"/order/{order_id}/cancel",
        headers=auth_headers(customer_token),
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"].lower() == "cancelled"

    db.expire_all()

    inventory_after = (
        inventory_repository.get_inventory_by_product_id(product_id)
    )

    assert inventory_after.reserved_quantity == reserved_before - 1
    assert inventory_after.total_quantity == total_before


def test_customer_cannot_cancel_order_twice(client, db):
    admin_token = create_admin_and_get_token(client, db)
    customer_token = register_customer_and_get_token(client)

    product_id = create_product_with_inventory(client, admin_token)
    order_id = create_order(client, customer_token, product_id)

    first_response = client.patch(
        f"/order/{order_id}/cancel",
        headers=auth_headers(customer_token),
    )

    assert first_response.status_code == 200, first_response.text
    assert first_response.json()["status"].lower() == "cancelled"

    inventory_repository = InventoryRepository(db)
    db.expire_all()

    inventory_after_first = (
        inventory_repository.get_inventory_by_product_id(product_id)
    )
    reserved_after_first = inventory_after_first.reserved_quantity
    total_after_first = inventory_after_first.total_quantity

    second_response = client.patch(
        f"/order/{order_id}/cancel",
        headers=auth_headers(customer_token),
    )

    assert second_response.status_code == 409, second_response.text
    assert (
        second_response.json()["error_code"]
        == "INVALID_ORDER_STATUS_TRANSITION"
    )

    db.expire_all()

    inventory_after_second = (
        inventory_repository.get_inventory_by_product_id(product_id)
    )

    assert (
        inventory_after_second.reserved_quantity
        == reserved_after_first
    )
    assert (
        inventory_after_second.total_quantity
        == total_after_first
    )