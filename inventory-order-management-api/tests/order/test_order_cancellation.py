import uuid
import pytest

from decimal import Decimal
from datetime import datetime

from tests.database import TestSessionLocal

from app.repositories.order_repository import OrderRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_item_repository import OrderItemRepository

from app.services.order_service import OrderService

from app.models.customer import Customer
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.category import Category

from app.constants.order_constants import OrderStatus

from app.exceptions.order_exceptions import InvalidOrderStatusTransitionError, OrderNotFoundError

@pytest.fixture
def cancellation_setup():

    db = TestSessionLocal()

    order_repository = OrderRepository(db)
    customer_repository = CustomerRepository(db)
    product_repository = ProductRepository(db)
    inventory_repository = InventoryRepository(db)
    order_item_repository = OrderItemRepository(db)

    service = OrderService(
        order_repository=order_repository,
        customer_repository=customer_repository,
        product_repository=product_repository,
        inventory_repository=inventory_repository,
        order_item_repository=order_item_repository
    )

    unique_id = uuid.uuid4().hex[:8]

    customer = Customer(
        name="Cancellation Test Customer",
        email=f"cancel_{unique_id}@example.com",
        phone=f"98765{str(uuid.uuid4().int)[-5:]}"
    )

    db.add(customer)
    db.flush()

    category = Category(
        name=f"Cancellation Category {unique_id}"
    )

    db.add(category)
    db.flush()

    product = Product(
    name=f"Cancellation Product {unique_id}",
    price=Decimal("100.00"),
    category_id=category.id
)

    db.add(product)
    db.flush()

    inventory = Inventory(
        product_id=product.id,
        total_quantity=10,
        reserved_quantity=3
    )

    db.add(inventory)
    db.flush()

    order = Order(
        order_number=f"TEST-CANCEL-{unique_id}",
        customer_id=customer.id,
        status=OrderStatus.PENDING,
        total_amount=Decimal("300.00"),
        reservation_until=datetime.now()
    )

    db.add(order)
    db.flush()

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_name=product.name,
        quantity=3,
        unit_price=product.price
    )

    db.add(order_item)

    db.commit()

    return db, service, order, inventory


def test_cancel_confirmed_order_is_rejected(cancellation_setup):
    db, service, order, inventory = cancellation_setup

    order.status = OrderStatus.CONFIRMED
    db.commit()

    with pytest.raises(InvalidOrderStatusTransitionError):
        service.cancel_order(order.id)

    db.refresh(order)
    db.refresh(inventory)

    assert order.status == OrderStatus.CONFIRMED
    assert inventory.reserved_quantity == 3
    
    

def test_cancel_shipped_order_id_rejected(cancellation_setup):
    
    db,service, order, inventory = cancellation_setup
    
    order.status = OrderStatus.SHIPPED
    db.commit()
    
    with pytest.raises(InvalidOrderStatusTransitionError):
        service.cancel_order(order.id)

    db.refresh(order)
    db.refresh(inventory)

    assert order.status == OrderStatus.SHIPPED
    assert inventory.reserved_quantity == 3
    
    

def test_cancel_delivered_order_is_rejected(cancellation_setup):
    
    db,service, order, inventory = cancellation_setup
    
    order.status = OrderStatus.DELIVERED
    db.commit()

    with pytest.raises(InvalidOrderStatusTransitionError):
        
        service.cancel_order(order.id)

    db.refresh(order)
    db.refresh(inventory)

    assert order.status == OrderStatus.DELIVERED
    assert inventory.reserved_quantity == 3
    



def test_cancel_expired_order_is_rejected(cancellation_setup):
    
    db,service, order, inventory = cancellation_setup
    
    order.status = OrderStatus.EXPIRED
    db.commit()

    with pytest.raises(InvalidOrderStatusTransitionError):
        
        service.cancel_order(order.id)

    db.refresh(order)
    db.refresh(inventory)

    assert order.status == OrderStatus.EXPIRED
    assert inventory.reserved_quantity == 3
    



def test_cancel_pending_order_releases_inventory(cancellation_setup):
    db, service, order, inventory = cancellation_setup

    service.cancel_order(order.id)

    db.refresh(order)
    db.refresh(inventory)

    assert order.status == OrderStatus.CANCELLED
    assert inventory.reserved_quantity == 0
    assert inventory.available_quantity == 10
    
    


def test_cancel_already_cancelled_order_is_rejected(cancellation_setup):
    db, service, order, inventory = cancellation_setup

    order.status = OrderStatus.CANCELLED
    db.commit()

    with pytest.raises(InvalidOrderStatusTransitionError):
        service.cancel_order(order.id)

    db.refresh(order)
    db.refresh(inventory)

    assert order.status == OrderStatus.CANCELLED
    assert inventory.reserved_quantity == 3
    
    
    

def test_cancel_non_existing_order_raises_error(cancellation_setup):
    
    db,service, order , inventory = cancellation_setup
    
    non_existing_order_id =9999999
    
    with pytest.raises(OrderNotFoundError):
        service.cancel_order(non_existing_order_id)

    assert order.status == OrderStatus.PENDING
    assert inventory.reserved_quantity == 3

    
    
    
def test_cancel_order_rolls_back_on_error(cancellation_setup,monkeypatch):
    
    db, service, order, inventory = cancellation_setup
    
    def raise_error(*args, **kwargs):
        
        raise ValueError("Simulated inventory failure")

    monkeypatch.setattr(service.inventory_repository, "get_inventory_for_update", raise_error)
    
    with pytest.raises(ValueError, match="Simulated inventory failure"):
        service.cancel_order(order.id)

    db.refresh(order)
    db.refresh(inventory)

    assert order.status == OrderStatus.PENDING
    assert inventory.reserved_quantity == 3
