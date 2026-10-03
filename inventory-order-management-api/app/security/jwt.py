from datetime import datetime, timedelta, timezone

from jose import jwt,JWTError

from app.core.config import settings


def create_access_token(
    user_id: int,
    role: str
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return token


def decode_access_token(token:str) -> dict:
    
    try :
        
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        
        return payload
    
    except JWTError:
        raise ValueError("Invalid or expired token")