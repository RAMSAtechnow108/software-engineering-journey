from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  
from sqlalchemy.orm import Session

from app.core.database import get_db 
from app.repositories.user_repository import UserRepository
from app.security.jwt import decode_access_token
from app.models.user import User
from app.exceptions.auth_exceptions import InvalidCredentialsError

from app.constants.user_constants import UserRole


security  = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db:Session= Depends(get_db)
) ->User:
    
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



def require_admin(current_user: User = Depends(get_current_user)) -> User:
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code = 403, detail="Admin access required")
    
    return current_user