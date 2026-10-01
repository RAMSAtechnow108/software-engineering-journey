from app.security.password import hash_password, verify_password


def test_password():
    
    password = "StrongPass123"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password) is True
    assert verify_password("WrongPasswrd", hashed_password) is False


