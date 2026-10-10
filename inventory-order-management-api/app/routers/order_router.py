from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.order_schema import OrderCreate, OrderResponse,OrderStatusUpdate
from app.services.order_service import OrderService

from app.repositories.order_repository import OrderRepository
from app.repositories.order_item_repository import OrderItemRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.product_repository import  ProductRepository
from app.repositories.inventory_repository import InventoryRepository

from app.security.dependencies import get_current_user

from app.models.user import User


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
def get_order_by_id(order_id:int,
                    current_user: User = Depends(get_current_user),service: OrderService = Depends(get_order_service)):
    return service.get_order_by_id(order_id, current_user=current_user)


@order_router.post(
    "/",
    response_model=OrderResponse,
    status_code=201
)
def create_order(
                 order_data: OrderCreate,
                 current_user: User= Depends(get_current_user),service:OrderService=Depends(get_order_service)):
    return service.create_order(customer_id=current_user.customer_id,order_data=order_data,current_user=current_user)


@order_router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id:int, 
    status_data: OrderStatusUpdate, 
    current_user: User=Depends(get_current_user),
    service:OrderService=Depends(get_order_service)
    ):
    return service.update_order_status(
        order_id=order_id, 
        new_status=status_data.status,
        current_user=current_user
        )


@order_router.patch("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id:int, 
    current_user: User =Depends(get_current_user),
    service: OrderService=Depends(get_order_service)
    ):
    
    return service.cancel_order(
        order_id,
        current_user=current_user
        )