import uuid

import pytest



def register_customer_and_get_token(client):
    """Register a unique customer and return their access token."""
    unique_id = uuid.uuid4().hex[:10]
    email = f"customer-{unique_id}@example.com"
    password = "CustomerPass123"
    phone = str(9_000_000_000 + uuid.uuid4().int % 999_999_999)

    register_response = client.post(
    "/users/register",
    json={
        "name": f"Test Customer {unique_id}",
        "email": email,
        "password": password,
        "phone": phone,
    },
)

    assert register_response.status_code in (200, 201), (
        register_response.text
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200, login_response.text

    return login_response.json()["access_token"]


def test_create_order_requires_authentication(client):
    response = client.post(
        "/order/",
        json={
            "items": [],
        },
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"items": []},
        {"items": [{"product_id": 1, "quantity": 0}]},
        {"items": [{"product_id": 1, "quantity": -1}]},
    ],
)
def test_create_order_rejects_invalid_payload(client, payload):
    token = register_customer_and_get_token(client)

    response = client.post(
        "/order/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code in (400, 422)


def test_create_order_rejects_insufficient_inventory(client, customer_token, admin_token):


    category_name = f"Test Category {uuid.uuid4().hex[:8]}"

    category_response = client.post(
        "/categories/",
        headers={"Authorization":f"Bearer {admin_token}"},
        json={"name": category_name},
    )

    assert category_response.status_code in (200, 201), (
        category_response.text
    )

    category_id = category_response.json()["id"]

    # Product create karne ke liye admin token zaroori hai.
    product_response = client.post(
        "/products/",
        json={
            "name": f"Test Product {uuid.uuid4().hex[:8]}",
            "description": "Test product",
            "price": 100.0,
            "category_id": category_id,
            "inventory":{"total_quantity": 1},
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert product_response.status_code in (200, 201), (
        product_response.text
    )

    product_id = product_response.json()["id"]

    # Inventory sirf 1 hai, lekin order quantity 2 hai.
    order_response = client.post(
        "/order/",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2,
                }
            ]
        },
        headers={"Authorization": f"Bearer {customer_token}"},
    )

    assert order_response.status_code == 409, order_response.text
    assert order_response.json()["error_code"] == "INSUFFICIENT_INVENTORY"


def test_customer_can_access_own_order_but_not_another_customers(
    client,admin_token
):
    # Do alag customers.
    customer_a_token = register_customer_and_get_token(client)
    customer_b_token = register_customer_and_get_token(client)


    category_name = f"Test Category {uuid.uuid4().hex[:8]}"

    category_response = client.post(
        "/categories/",
        headers={"Authorization":f"Bearer {admin_token}"},
        json={"name": category_name},
    )

    assert category_response.status_code in (200, 201), (
        category_response.text
    )

    category_id = category_response.json()["id"]

    product_response = client.post(
        "/products/",
        json={
            "name": f"Test Product {uuid.uuid4().hex[:8]}",
            "description": "Test product",
            "price": 100.0,
            "category_id": category_id,
            "inventory":{"total_quantity": 10},
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert product_response.status_code in (200, 201), (
        product_response.text
    )

    product_id = product_response.json()["id"]

    # Customer B apna order create karta hai.
    order_response = client.post(
        "/order/",
        json={
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                }
            ]
        },
        headers={"Authorization": f"Bearer {customer_b_token}"},
    )

    assert order_response.status_code in (200, 201), (
        order_response.text
    )

    order_id = order_response.json()["id"]

    # Customer B apna order access kar sakta hai.
    own_order_response = client.get(
        f"/order/{order_id}",
        headers={"Authorization": f"Bearer {customer_b_token}"},
    )

    assert own_order_response.status_code == 200

    # Customer A, customer B ka order access nahi kar sakta.
    other_order_response = client.get(
        f"/order/{order_id}",
        headers={"Authorization": f"Bearer {customer_a_token}"},
    )

    assert other_order_response.status_code == 403


def test_get_order_requires_authentication(client):
    response = client.get("/order/1")

    assert response.status_code == 401


def test_get_nonexistent_order_returns_404(client):
    token = register_customer_and_get_token(client)

    response = client.get(
        "/order/999999999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404