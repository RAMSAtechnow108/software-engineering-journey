
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select

from tests.database import TestSessionLocal

from app.repositories.order_repository import OrderRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_item_repository import OrderItemRepository

from app.services.order_service import OrderService

from app.models.customer import Customer
from app.models.order import Order, OrderStatus
from app.models.category import Category
from app.models.inventory import Inventory
from app.models.order_item import OrderItem
from app.models.product import Product


def unique_suffix():
    return uuid.uuid4().hex[:10]


def create_order_service(db):
    return OrderService(
        order_repository=OrderRepository(db),
        customer_repository=CustomerRepository(db),
        product_repository=ProductRepository(db),
        inventory_repository=InventoryRepository(db),
        order_item_repository=OrderItemRepository(db),
    )


def create_customer(db, suffix):
    customer = Customer(
        name=f"Expiry Test Customer {suffix}",
        email=f"expiry_{suffix}@example.com",
        phone=f"9{uuid.uuid4().int % 10**9:09d}",
    )
    db.add(customer)
    db.flush()
    return customer


def create_category(db, suffix):
    category = Category(name=f"Expiry Category {suffix}")
    db.add(category)
    db.flush()
    return category


def create_product(db, category_id, name, price):
    product = Product(
        name=name,
        price=Decimal(price),
        category_id=category_id,
    )
    db.add(product)
    db.flush()
    return product


def test_get_expired_orders():
    db = TestSessionLocal()
    suffix = unique_suffix()

    try:
        repository = OrderRepository(db)
        customer = create_customer(db, suffix)
        current_time = datetime.now()

        expired_order = Order(
            order_number=f"TEST-EXPIRED-{suffix}",
            customer_id=customer.id,
            status=OrderStatus.PENDING,
            total_amount=Decimal("0.00"),
            reservation_until=current_time - timedelta(minutes=1),
        )

        future_order = Order(
            order_number=f"TEST-FUTURE-{suffix}",
            customer_id=customer.id,
            status=OrderStatus.PENDING,
            total_amount=Decimal("0.00"),
            reservation_until=current_time + timedelta(minutes=10),
        )

        confirmed_order = Order(
            order_number=f"TEST-CONFIRMED-{suffix}",
            customer_id=customer.id,
            status=OrderStatus.CONFIRMED,
            total_amount=Decimal("0.00"),
            reservation_until=current_time - timedelta(minutes=1),
        )

        db.add_all([expired_order, future_order, confirmed_order])
        db.flush()

        expired_order_id = expired_order.id

        expired_orders = repository.get_expired_orders(current_time)
        expired_order_numbers = {
            order.order_number for order in expired_orders
        }

        # Verify the target expired order is returned.
        assert expired_order.order_number in expired_order_numbers

        # A future order and a confirmed order must not be returned.
        assert future_order.order_number not in expired_order_numbers
        assert confirmed_order.order_number not in expired_order_numbers

        # Verify that the repository can fetch the order for update.
        locked_order = repository.get_order_for_update(expired_order_id)

        assert locked_order is not None
        assert locked_order.id == expired_order_id

    finally:
        db.close()


def test_expire_order():
    db = TestSessionLocal()
    suffix = unique_suffix()

    try:
        service = create_order_service(db)

        customer = create_customer(db, suffix)
        category = create_category(db, suffix)

        product = create_product(
            db=db,
            category_id=category.id,
            name=f"Expiry Product {suffix}",
            price="100.00",
        )

        inventory = Inventory(
            product_id=product.id,
            total_quantity=10,
            reserved_quantity=3,
        )
        db.add(inventory)
        db.flush()

        current_time = datetime.now()

        order = Order(
            order_number=f"TEST-EXPIRY-ORDER-{suffix}",
            customer_id=customer.id,
            status=OrderStatus.PENDING,
            total_amount=Decimal("300.00"),
            reservation_until=current_time - timedelta(minutes=1),
        )
        db.add(order)
        db.flush()

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            quantity=3,
            unit_price=product.price,
        )
        db.add(order_item)
        db.commit()

        order_id = order.id
        inventory_id = inventory.id

        service.expire_orders(current_time)

        db.expire_all()

        updated_order = db.get(Order, order_id)
        updated_inventory = db.get(Inventory, inventory_id)

        assert updated_order.status == OrderStatus.EXPIRED
        assert updated_inventory.reserved_quantity == 0
        assert updated_inventory.total_quantity == 10

    finally:
        db.close()


def test_expired_order_rollback():
    db = TestSessionLocal()
    suffix = unique_suffix()

    try:
        service = create_order_service(db)

        customer = create_customer(db, suffix)
        category = create_category(db, suffix)

        product_a = create_product(
            db=db,
            category_id=category.id,
            name=f"Rollback Product A {suffix}",
            price="100.00",
        )

        product_b = create_product(
            db=db,
            category_id=category.id,
            name=f"Rollback Product B {suffix}",
            price="200.00",
        )

        inventory_a = Inventory(
            product_id=product_a.id,
            total_quantity=10,
            reserved_quantity=2,
        )

        inventory_b = Inventory(
            product_id=product_b.id,
            total_quantity=10,
            reserved_quantity=1,
        )

        db.add_all([inventory_a, inventory_b])
        db.flush()

        current_time = datetime.now()

        order = Order(
            order_number=f"TEST-ROLLBACK-ORDER-{suffix}",
            customer_id=customer.id,
            status=OrderStatus.PENDING,
            total_amount=Decimal("800.00"),
            reservation_until=current_time - timedelta(minutes=1),
        )

        db.add(order)
        db.flush()

        order_item_a = OrderItem(
            order_id=order.id,
            product_id=product_a.id,
            product_name=product_a.name,
            quantity=2,
            unit_price=product_a.price,
        )

        # Quantity 3 exceeds the reserved stock of 1.
        # This should cause expiration to fail and roll back.
        order_item_b = OrderItem(
            order_id=order.id,
            product_id=product_b.id,
            product_name=product_b.name,
            quantity=3,
            unit_price=product_b.price,
        )

        db.add_all([order_item_a, order_item_b])
        db.commit()

        order_id = order.id
        inventory_a_id = inventory_a.id
        inventory_b_id = inventory_b.id

        with pytest.raises(ValueError):
            service.expire_orders(current_time)

        db.expire_all()

        order_after = db.get(Order, order_id)
        inventory_a_after = db.get(Inventory, inventory_a_id)
        inventory_b_after = db.get(Inventory, inventory_b_id)

        # Verify that the failed operation changed nothing.
        assert order_after.status == OrderStatus.PENDING
        assert inventory_a_after.reserved_quantity == 2
        assert inventory_b_after.reserved_quantity == 1

        assert inventory_a_after.total_quantity == 10
        assert inventory_b_after.total_quantity == 10

    finally:
        db.close()
