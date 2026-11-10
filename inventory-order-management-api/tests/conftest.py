import pytest
import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import get_db
from tests.database import TestSessionLocal

from app.repositories.user_repository import UserRepository
from app.security.password import hash_password


@pytest.fixture
def db():
    db: Session = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally :
            pass
        
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear()
    
    
    
    

@pytest.fixture
def customer_token(client):
    suffix = uuid.uuid4().hex[:10]
    email = f"customer-{suffix}@example.com"
    phone = str(9_000_000_000+uuid.uuid4().int % 999_999_999)
    password = "StrongPass123"

    
    registration_response = client.post(
        "/users/register",
        json={
            "name":f"Test Customer {suffix}",
            "email":email,
            "phone":phone,
            "password":password
        }
    )

    assert registration_response.status_code == 201, registration_response.text
    
    login_response = client.post(
        "/auth/login",
        json={"email":email, "password":password}
    )
    
    assert login_response.status_code == 200, login_response.text
    
    return login_response.json()["access_token"]



@pytest.fixture
def admin_token(client,db):
    email=f"test-admin-{uuid.uuid4().hex[:10]}@example.com"
    password = "AdminPass123"


    user_repository = UserRepository(db)
    user_repository.create_admin_user(email=email, password_hash=hash_password(password=password))

    db.commit()

    login_response = client.post(
        "/auth/login",
        json={"email":email, "password":password}
    )

    assert login_response.status_code == 200, login_response.text
    return login_response.json()["access_token"]