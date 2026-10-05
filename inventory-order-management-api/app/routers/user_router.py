from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.repositories.user_repository import UserRepository
from app.repositories.customer_repository import CustomerRepository

from app.services.user_service import UserService

from app.security.dependencies import require_admin
from app.models.user import User

from app.schemas.user_schema import UserCreate, UserRegistrationResponse, UserResponse

user_router = APIRouter()


def get_user_service(db:Session=Depends(get_db)):
    
    user_repository = UserRepository(db)
    customer_repository = CustomerRepository(db)

    service = UserService(user_repository=user_repository, customer_repository=customer_repository)

    return service


@user_router.post("/register", response_model=UserRegistrationResponse, status_code=201)
def register_customer(user_data:UserCreate, service:UserService = Depends(get_user_service)):
    
    user, customer = service.register_customer(user_data)

    return {"user": user, "customer":customer}


@user_router.get("/", response_model=list[UserResponse])
def get_all_users(current_user: User= Depends(require_admin), service: UserService = Depends(get_user_service)):
    return service.get_all_users()