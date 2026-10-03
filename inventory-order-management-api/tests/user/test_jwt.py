from app.security.jwt import create_access_token, decode_access_token
from jose import jwt, JWTError
from app.core.config import settings


from datetime import datetime, timedelta, timezone
import pytest


def test_create_access_token():
    token =create_access_token(user_id=4, role="customer")

    assert token is not None
    assert isinstance(token, str)
    assert len(token)>0
    
    
    
def test_access_token_payload():
    token = create_access_token(user_id=6,role="customer")

    payload = jwt.decode(token, settings.jwt_secret_key,algorithms=[settings.jwt_algorithm])

    assert payload["sub"]=="6"
    assert payload["role"] == "customer"
    assert "exp" in payload


def test_expired_access_token():
    expired_payload = {
        "sub":"6" ,
        "role":"customer",
        "exp":datetime.now(timezone.utc)-timedelta(minutes=1)
    }
    
    expired_token = jwt.encode(expired_payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    with pytest.raises(JWTError):
        jwt.decode(expired_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

        
    
    
def test_decode_access_token():
    token = create_access_token(user_id=6, role="customer")

    payload = decode_access_token(token)
    
    assert payload["sub"] == "6"
    assert payload["role"] == "customer"
    assert "exp" in payload
    


def test_decode_invalid_access_token():
    
    invalid_token = "this.is.no.a.valid.jwt"

    
    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_access_token(invalid_token)
