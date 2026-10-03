from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.schemas.auth_schema import LoginRequest

from app.security.dependencies import get_current_user
from app.schemas.user_schema import UserResponse
from app.models.user import User


auth_router = APIRouter()


def get_auth_service(db:Session=Depends(get_db)):
    user_repository = UserRepository(db)

    service = AuthService(user_repository=user_repository)
    return service


@auth_router.post("/login")
def login(login_data:LoginRequest, service: AuthService=Depends(get_auth_service)):
    
    access_token = service.authenticate_user(login_data)

    return {
        "access_token":access_token,"token_type":"bearer"
    }


@auth_router.get("/me", response_model=UserResponse)
def get_me(current_user:User=Depends(get_current_user)):
    return current_user
