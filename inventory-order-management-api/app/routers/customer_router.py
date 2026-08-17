from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.repositories.customer_repository import CustomerRepository
from app.services.customer_service import CustomerService

from app.schemas.customer_schema import CustomerResponse,CustomerCreate,CustomerUpdate


customer_router = APIRouter()


def get_customer_service(db: Session = Depends(get_db)):
    
    repository = CustomerRepository(db)

    service = CustomerService(repository)

    return service


@customer_router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer_by_id(customer_id: int, service:CustomerService = Depends(get_customer_service)):
    return service.get_customer_by_id(customer_id)


@customer_router.post("/", response_model=CustomerResponse)
def create_customer(customer: CustomerCreate, service:CustomerService = Depends(get_customer_service)):
    return service.create_customer(customer)

@customer_router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id:int, customer_data:CustomerUpdate, service:CustomerService=Depends(get_customer_service)):
    return service.update_customer(customer_id, customer_data)