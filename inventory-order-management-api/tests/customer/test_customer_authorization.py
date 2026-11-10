import uuid


def register_and_login_customer(client, name):
    unique_id = uuid.uuid4().hex

    email = f"{unique_id}@example.com"
    phone = str(uuid.uuid4().int % 10**10).zfill(10)
    password = "StrongPass123"

    registration_response = client.post(
        "/users/register",
        json={
            "name": name,
            "email": email,
            "phone": phone,
            "password": password,
        },
    )

    assert registration_response.status_code == 201, (
        registration_response.text
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    profile_response = client.get(
        "/customer/me",
        headers=headers,
    )

    assert profile_response.status_code == 200, profile_response.text

    customer_id = profile_response.json()["id"]

    return headers, customer_id


def test_customer_can_update_own_profile(client):
    headers, customer_id = register_and_login_customer(
        client,
        "Customer A",
    )

    response = client.patch(
        "/customer/me",
        headers=headers,
        json={
            "name": "Updated Customer A",
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["id"] == customer_id
    assert data["name"] == "Updated Customer A"



def test_customer_cannot_update_another_customer(client):
    headers_a, customer_a_id = register_and_login_customer(
        client,
        "Customer A",
    )

    headers_b, customer_b_id = register_and_login_customer(
        client,
        "Customer B",
    )

    response = client.patch(
        f"/customer/{customer_b_id}",
        headers=headers_a,
        json={"name": "Hacked Name"},
    )

    assert response.status_code == 403, response.text



def test_customer_cannot_update_profile_without_token(client):
    response = client.patch(
        "/customer/me",
        json={
            "name": "Unauthorized Customer",
        },
    )

    assert response.status_code in (401, 403)


def test_customer_update_rejects_empty_body(client):
    headers, _ = register_and_login_customer(
        client,
        "Empty Body Customer",
    )

    response = client.patch(
        "/customer/me",
        headers=headers,
        json={},
    )

    assert response.status_code == 422


def test_customer_update_rejects_null_name(client):
    headers, _ = register_and_login_customer(
        client,
        "Null Name Customer",
    )

    response = client.patch(
        "/customer/me",
        headers=headers,
        json={
            "name": None,
        },
    )

    assert response.status_code == 422