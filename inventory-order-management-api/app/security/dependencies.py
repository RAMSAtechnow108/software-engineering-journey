from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  
from sqlalchemy.orm import Session

from app.core.database import get_db 
from app.repositories.user_repository import UserRepository
from app.security.jwt import decode_access_token
from app.models.user import User
from app.exceptions.auth_exceptions import InvalidCredentialsError


security  = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db:Session= Depends(get_db)
):
    
    token = credentials.credentials
    
    try:
        payload = decode_access_token(token)
    except ValueError:
        raise InvalidCredentialsError()

    user_id = payload.get("sub")

    if user_id is None:
        raise InvalidCredentialsError()

    user_repository = UserRepository(db)

    user = user_repository.get_user_by_id(user_id)
    
    if user is None:
        raise  InvalidCredentialsError()

    if not user.is_active:
        raise InvalidCredentialsError()

    return user