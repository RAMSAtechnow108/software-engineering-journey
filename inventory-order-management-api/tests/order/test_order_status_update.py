import uuid
import pytest

from decimal import Decimal
from datetime import datetime

from tests.database import TestSessionLocal

from app.repositories.order_repository import OrderRepository
from app.repositories.customer_repository import CustomerRepository

from app.services.order_service import OrderService

from app.models.customer import Customer
from app.models.order import Order
from app.models.order import OrderStatus

from app.exceptions.order_exceptions import InvalidOrderStatusTransitionError


@pytest.fixture
def order_service():
    db = TestSessionLocal()

    order_repository = OrderRepository(db)
    customer_repository = CustomerRepository(db)

    service = OrderService(
        order_repository=order_repository,
        customer_repository=customer_repository,
        product_repository=None,
        inventory_repository=None,
        order_item_repository=None
    )

    yield db, service

    db.close()


@pytest.fixture
def pending_order(order_service):
    db, service = order_service

    unique_id = uuid.uuid4().hex[:8]

    customer = Customer(
        name="Status Test Customer",
        email=f"pending_status_{unique_id}@example.com",
        phone=f"98765{str(uuid.uuid4().int)[-5:]}"
    )

    db.add(customer)
    db.flush()

    order = Order(
        order_number=f"TEST-PENDING-STATUS-{unique_id}",
        customer_id=customer.id,
        status=OrderStatus.PENDING,
        total_amount=Decimal("100.00"),
        reservation_until=datetime.now()
    )

    db.add(order)
    db.commit()

    return db, service, order


def test_update_order_status_to_confirmed(pending_order):
    db, service, order = pending_order

    updated_order = service.update_order_status(
        order_id=order.id,
        new_status=OrderStatus.CONFIRMED
    )

    assert updated_order.status == OrderStatus.CONFIRMED


def test_invalid_order_status_transition(pending_order):
    db, service, order = pending_order

    with pytest.raises(InvalidOrderStatusTransitionError):
        service.update_order_status(
            order_id=order.id,
            new_status=OrderStatus.SHIPPED
        )

    db.refresh(order)

    assert order.status == OrderStatus.PENDING


def test_update_confirmed_order_to_shipped(pending_order):
    db, service, order = pending_order

    order.status = OrderStatus.CONFIRMED
    db.commit()

    updated_order = service.update_order_status(
        order_id=order.id,
        new_status=OrderStatus.SHIPPED
    )

    assert updated_order.status == OrderStatus.SHIPPED


def test_update_shipped_order_to_delivered(pending_order):
    db, service, order = pending_order

    order.status = OrderStatus.SHIPPED
    db.commit()

    updated_order = service.update_order_status(
        order_id=order.id,
        new_status=OrderStatus.DELIVERED
    )

    assert updated_order.status == OrderStatus.DELIVERED


def test_delivered_order_cannot_transition(pending_order):
    db, service, order = pending_order

    order.status = OrderStatus.DELIVERED
    db.commit()

    with pytest.raises(InvalidOrderStatusTransitionError):
        service.update_order_status(
            order_id=order.id,
            new_status=OrderStatus.PENDING
        )

    db.refresh(order)

    assert order.status == OrderStatus.DELIVERED
    
    

def test_complete_order_lifecycle(pending_order):
    
    db, service, order = pending_order

    order = service.update_order_status(order_id=order.id,new_status=OrderStatus.CONFIRMED)

    assert order.status == OrderStatus.CONFIRMED
    
    order = service.update_order_status(order_id=order.id, new_status=OrderStatus.SHIPPED)

    assert order.status == OrderStatus.SHIPPED

    order =service.update_order_status(order_id=order.id, new_status=OrderStatus.DELIVERED)

    assert order.status == OrderStatus.DELIVERED