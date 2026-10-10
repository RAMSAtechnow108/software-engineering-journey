
import uuid

from app.models.user import User
from app.models.customer import Customer
from app.security.password import hash_password


def test_login_wrong_password(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "testuser123@example.com",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["error_code"] == "INVALID_CREDENTIALS"
    assert data["message"] == "Invalid email or password"


def test_login_unkwonn_email(client):
    response = client.post(
        "/auth/login",
        json={
            "email": f"unknown_{uuid.uuid4().hex}@example.com",
            "password": "StrongPass123",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["error_code"] == "INVALID_CREDENTIALS"
    assert data["message"] == "Invalid email or password"


def test_login_inactive_user(client, db):
    unique_id = uuid.uuid4().hex
    email = f"inactive_{unique_id}@example.com"
    phone = f"9{uuid.uuid4().int % 1_000_000_000:09d}"
    password = "StrongPass123"

    # 1. Create the customer required by the User relationship.
    customer = Customer(
        name="Inactive Test Customer",
        email=email,
        phone=phone,
    )

    db.add(customer)
    db.flush()

    # 2. Create an inactive user with a valid password hash.
    user = User(
        email=email,
        password_hash=hash_password(password),
        is_active=False,
        role="CUSTOMER",
        customer_id=customer.id,
    )

    db.add(user)
    db.commit()

    # 3. Attempt login using the same email and correct password.
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["error_code"] == "INVALID_CREDENTIALS"
    assert data["message"] == "Invalid email or password"

