from app.models.customer import Customer
from app.models.user import User
from app.constants.user_constants import UserRole
from app.security.password import verify_password



def test_sucessful_customer_registration(client, db):
    
    response = client.post(
        "/users/register",
        json={
            "name": "Test User",
            "email": "testuser123@example.com",
            "phone": "90000000003",
            "password": "StrongPass123"
        }        
    )
    
    assert response.status_code == 201
    
    data = response.json()

    assert "user" in data
    assert "customer" in data

    assert data["user"]["email"] == "testuser123@example.com"
    assert data["user"]["role"] == "customer"
    assert data["user"]["is_active"] is True
    
    assert data["customer"]["name"] == "Test User"
    assert data["customer"]["email"] == "testuser123@example.com"
    assert data["customer"]["phone"] == "90000000003"
    
    
    user = (db.query(User).filter(User.email == "testuser123@example.com").first())
    
    customer = (
        db.query(Customer).filter(Customer.email == "testuser123@example.com").first()
    )
    
    assert user is not None
    assert customer is not None
    
    
    assert user.customer_id == customer.id
    
    assert user.password_hash != "StrongPass123"
    assert verify_password("StrongPass123",user.password_hash) is True
    
    assert user.role == UserRole.CUSTOMER
    assert user.is_active is True
    
def test_duplicate_customer_email(client):
    payload = {
        "name": "First User",
        "email": "duplicate@example.com",
        "phone": "9000000002",
        "password": "StrongPass123"
    }

    first_response = client.post(
        "/users/register",
        json=payload
    )

    assert first_response.status_code == 201

    second_payload = {
        "name": "Second User",
        "email": "duplicate@example.com",
        "phone": "9000000003",
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
    payload = {
        "name": "Phone User",
        "email": "phoneuser1@example.com",
        "phone": "9000000010",
        "password": "StrongPass123"
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
    response = client.post(
        "/users/register",
        json={
            "name": "Security Test",
            "email": "security@example.com",
            "phone": "9000000040",
            "password": "StrongPass123",
            "role": "admin",
            "customer_id": 999
        }
    )

    assert response.status_code == 201

    data = response.json()

    # Server must assign CUSTOMER role
    assert data["user"]["role"] == "customer"

    # User must be linked to the newly-created customer,
    # not to the client-supplied customer_id
    assert data["user"]["customer_id"] == data["customer"]["id"]

    assert data["user"]["customer_id"] != 999

    user = (
        db.query(User)
        .filter(User.email == "security@example.com")
        .first()
    )

    assert user is not None
    assert user.role == UserRole.CUSTOMER
    assert user.customer_id == data["customer"]["id"]