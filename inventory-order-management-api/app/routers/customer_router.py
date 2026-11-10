
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.constants.user_constants import UserRole
from app.repositories.customer_repository import CustomerRepository
from app.services.customer_service import CustomerService
from app.schemas.customer_schema import (
    CustomerResponse,
    CustomerCreate,
    CustomerUpdate,
)
from app.security.dependencies import get_current_user


customer_router = APIRouter()


def get_customer_service(
    db: Session = Depends(get_db),
) -> CustomerService:
    repository = CustomerRepository(db)
    return CustomerService(repository)


@customer_router.get("/me", response_model=CustomerResponse)
def get_my_customer_profile(
    current_user: User = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    if current_user.customer_id is None:
        raise HTTPException(
            status_code=403,
            detail="No customer profile associated with this account",
        )

    return service.get_customer_by_id(current_user.customer_id)


@customer_router.patch("/me", response_model=CustomerResponse)
def update_my_customer_profile(
    customer_data: CustomerUpdate,
    current_user: User = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    if current_user.customer_id is None:
        raise HTTPException(
            status_code=403,
            detail="No customer profile associated with this account",
        )

    return service.update_customer(
        current_user.customer_id,
        customer_data,
    )


@customer_router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer_by_id(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return service.get_customer_by_id(customer_id)


@customer_router.post("/", response_model=CustomerResponse)
def create_customer(
    customer: CustomerCreate,
    service: CustomerService = Depends(get_customer_service),
):
    return service.create_customer(customer)


@customer_router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    current_user: User = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return service.update_customer(customer_id, customer_data)
