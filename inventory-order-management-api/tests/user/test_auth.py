from app.models.user import User


def test_login_wrong_password(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "testuser123@example.com",
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["error_code"] == "INVALID_CREDENTIALS"
    assert data["message"] == "Invalid email or password"
    

def test_login_unkwonn_email(client):
    response = client.post(
        "/auth/login",
        json={
            "email":"doesnotexist@gmail.com",
            "password" :"StrongPass123"
        }
    )
    
    assert response.status_code==401
    
    data = response.json()

    assert data["error_code"] == "INVALID_CREDENTIALS"
    assert data["message"] == "Invalid email or password"
    
    


def test_login_inactive_user(client,db):
    
    
    user = (
        db.query(User).filter(User.email == "Testuser123@example.com").first()
    )


    assert user is not None
    
    user.is_active = False
    
    db.commit()

    response = client.post(
        "/auth/login",
        json = {
            "email":"testuser123@gmail.com",
            "password":"StrongPass123"
        }
    )
    
    assert response.status_code == 401
    data = response.json()

    assert data["error_code"] == "INVALID_CREDENTIALS"
    assert data["message"] == "Invalid email or password"
    