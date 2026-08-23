from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.order_schema import OrderCreate, OrderResponse
from app.services.order_service import OrderService

from app.repositories.order_repository import OrderRepository
from app.repositories.order_item_repository import OrderItemRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.product_repository import  ProductRepository
from app.repositories.inventory_repository import InventoryRepository


order_router = APIRouter()

def get_order_service(db: Session = Depends(get_db)):

    order_repository = OrderRepository(db)
    order_item_repository = OrderItemRepository(db)
    customer_repository = CustomerRepository(db)
    product_repository = ProductRepository(db)
    inventory_repository = InventoryRepository(db)

    service = OrderService(
        order_repository=order_repository,
        order_item_repository=order_item_repository,
        customer_repository=customer_repository,
        product_repository=product_repository,
        inventory_repository=inventory_repository,
    )

    return service

@order_router.get("/{order_id}", response_model=OrderResponse)
def get_order_by_id(order_id:int, service: OrderService = Depends(get_order_service)):
    return service.get_order_by_id(order_id)


@order_router.post(
    "/{customer_id}",
    response_model=OrderResponse,
    status_code=201
)
def create_order(customer_id:int, order_data: OrderCreate,service:OrderService=Depends(get_order_service)):
    return service.create_order(customer_id,order_data)

