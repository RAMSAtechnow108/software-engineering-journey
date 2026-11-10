from app.models.customer import Customer
from app.models.user import User
from app.constants.user_constants import UserRole
from app.security.password import verify_password
import uuid


def test_sucessful_customer_registration(client, db):
    email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
    phone = f"9{uuid.uuid4().int % 10**9:09d}"
    password = "StrongPass123"
    response = client.post(
        "/users/register",
        json={
            "name": "Test User",
            "email": email,
            "phone": phone,
            "password": password
        }        
    )
    
    assert response.status_code == 201
    
    data = response.json()
    

    assert "user" in data
    assert "customer" in data

    assert data["user"]["email"] == email
    assert data["user"]["role"] == "customer"
    assert data["user"]["is_active"] is True
    
    assert data["customer"]["name"] == "Test User"
    assert data["customer"]["email"] == email
    assert data["customer"]["phone"] == phone
    
    
    user = (db.query(User).filter(User.email == email).first())
    
    customer = (
        db.query(Customer).filter(Customer.email == email).first()
    )
    
    assert user is not None
    assert customer is not None
    
    
    assert user.customer_id == customer.id
    
    assert user.password_hash != password
    assert verify_password(password,user.password_hash) is True
    
    assert user.role == UserRole.CUSTOMER
    assert user.is_active is True
    
def test_duplicate_customer_email(client):
    email = f"test_duplicate_user_{uuid.uuid4().hex[:8]}@example.com"
    phone = f"9{uuid.uuid4().int % 10**9:09d}"
    password = "StrongPass123"
    payload = {
        "name": "First User",
        "email": email,
        "phone": phone,
        "password": password
    }

    first_response = client.post(
        "/users/register",
        json=payload
    )

    assert first_response.status_code == 201
    phone = f"9{uuid.uuid4().int % 10**9:09d}"
    second_payload = {
        "name": "Second User",
        "email": email,
        "phone": phone,
        "password": "AnotherPass123"
    }

    second_response = client.post(
        "/users/register",
        json=second_payload
    )

    assert second_response.status_code == 409

    data = second_response.json()

    assert data["error_code"] == "DUPLICATE_CUSTOMER_EMAIL"
    
    

def test_duplicate_customer_phone(client):
    email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
    phone = f"9{uuid.uuid4().int % 10**9:09d}"
    password = "StrongPass123"
    payload = {
        "name": "Phone User",
        "email": email,
        "phone": phone,
        "password": phone
    }

    first_response = client.post(
        "/users/register",
        json=payload
    )

    assert first_response.status_code == 201

    second_payload = {
        "name": "Another Phone User",
        "email": "phoneuser2@example.com",
        "phone": "9000000010",
        "password": "AnotherPass123"
    }

    second_response = client.post(
        "/users/register",
        json=second_payload
    )

    assert second_response.status_code == 409

    data = second_response.json()

    assert data["error_code"] == "DUPLICATE_CUSTOMER_PHONE"
    
    
    
def test_registration_invalid_email(client):
    phone = f"9{uuid.uuid4().int % 10**9:09d}"
    
    response = client.post(
        "/users/register",
        json={
            "name": "Invalid Email",
            "email": "not-an-email",
            "phone": "9000000020",
            "password": "StrongPass123"
        }
    )

    assert response.status_code == 422
def test_registration_short_password(client):
    phone = f"9{uuid.uuid4().int % 10**9:09d}"
    
    response = client.post(
        "/users/register",
        json={
            "name": "Short Password",
            "email": "shortpass@example.com",
            "phone": "9000000021",
            "password": "123"
        }
    )

    assert response.status_code == 422
def test_registration_short_name(client):
    
    response = client.post(
        "/users/register",
        json={
            "name": "AB",
            "email": "shortname@example.com",
            "phone": "9000000022",
            "password": "StrongPass123"
        }
    )

    assert response.status_code == 422
    
    

def test_registration_cannot_assign_admin_role(client, db):
    email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
    phone = f"9{uuid.uuid4().int % 10**9:09d}"
    password = "StrongPass123"
    response = client.post(
        "/users/register",
        json={
            "name": "Security Test",
            "email": email,
            "phone": phone,
            "password": password,
            "role": "admin",
            "customer_id": 999
        }
    )

    assert response.status_code == 201

    data = response.json()


    assert data["user"]["role"] == "customer"
    assert data["user"]["customer_id"] == data["customer"]["id"]

    assert data["user"]["customer_id"] != 999

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    assert user is not None
    assert user.role == UserRole.CUSTOMER
    assert user.customer_id == data["customer"]["id"]