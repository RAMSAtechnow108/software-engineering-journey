from app.exceptions.product_exceptions import ProductNotFoundError
from app.exceptions.inventory_exceptions import InsufficientInventoryError

import uuid
from decimal import Decimal

import pytest

from tests.database import TestSessionLocal

from app.models.customer import Customer
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.order import Order
from app.models.order_item import OrderItem

from app.constants.user_constants import UserRole
from app.schemas.order_schema import OrderCreate, OrderItemCreate

from app.repositories.order_repository import OrderRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_item_repository import OrderItemRepository

from app.services.order_service import OrderService


def test_create_order_rolls_back_when_order_item_creation_fails(
    monkeypatch,
):
    db = TestSessionLocal()

    try:
        unique_id = uuid.uuid4().hex[:10]

        # 1. Create customer
        customer = Customer(
            name=f"Creation Test Customer {unique_id}",
            email=f"creation_{unique_id}@example.com",
            phone=f"9{uuid.uuid4().int % 10**9:09d}",
        )
        db.add(customer)
        db.flush()

        # 2. Create customer user
        user = User(
            email=f"creation_user_{unique_id}@example.com",
            password_hash="test-password-hash",
            role=UserRole.CUSTOMER,
            is_active=True,
            customer_id=customer.id,
        )
        db.add(user)
        db.flush()

        # 3. Create category and product
        category = Category(
            name=f"Creation Category {unique_id}",
        )
        db.add(category)
        db.flush()

        product = Product(
            name=f"Creation Product {unique_id}",
            price=Decimal("100.00"),
            category_id=category.id,
        )
        db.add(product)
        db.flush()

        # 4. Create inventory with 10 available units
        inventory = Inventory(
            product_id=product.id,
            total_quantity=10,
            reserved_quantity=0,
        )
        db.add(inventory)
        db.commit()

        customer_id = customer.id
        product_id = product.id
        inventory_id = inventory.id

        # 5. Build service using the same DB session
        service = OrderService(
            order_repository=OrderRepository(db),
            customer_repository=CustomerRepository(db),
            product_repository=ProductRepository(db),
            inventory_repository=InventoryRepository(db),
            order_item_repository=OrderItemRepository(db),
        )

        # 6. Simulate failure during order-item creation
        def fail_order_item_creation(*args, **kwargs):
            raise RuntimeError("Simulated order-item failure")

        monkeypatch.setattr(
            service.order_item_repository,
            "create_order_item",
            fail_order_item_creation,
        )

        order_data = OrderCreate(
            items=[
                OrderItemCreate(
                    product_id=product_id,
                    quantity=2,
                )
            ]
        )

        # 7. Verify that the original error propagates
        with pytest.raises(
            RuntimeError,
            match="Simulated order-item failure",
        ):
            service.create_order(
                customer_id=customer_id,
                order_data=order_data,
                current_user=user,
            )

        # 8. Verify the persisted database state
        db.expire_all()

        final_inventory = db.get(Inventory, inventory_id)

        assert final_inventory.reserved_quantity == 0
        assert final_inventory.available_quantity == 10

        order_count = (
            db.query(Order)
            .filter(Order.customer_id == customer_id)
            .count()
        )
        assert order_count == 0

        order_item_count = (
            db.query(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(Order.customer_id == customer_id)
            .count()
        )
        assert order_item_count == 0

    finally:
        db.rollback()
        db.close()

    
    



def _create_order_context(db, product_specs):
    """
    product_specs format:
    [
        ("Product A", Decimal("100.00"), 10),
        ("Product B", Decimal("50.00"), 5),
    ]

    Har tuple: product name, unit price, total stock.
    """
    unique_id = uuid.uuid4().hex[:10]

    customer = Customer(
        name=f"Order Customer {unique_id}",
        email=f"order_customer_{unique_id}@example.com",
        phone=f"9{uuid.uuid4().int % 10**9:09d}",
    )
    db.add(customer)
    db.flush()

    user = User(
        email=f"order_user_{unique_id}@example.com",
        password_hash="test-password-hash",
        role=UserRole.CUSTOMER,
        is_active=True,
        customer_id=customer.id,
    )
    db.add(user)

    category = Category(name=f"Order Category {unique_id}")
    db.add(category)
    db.flush()

    products = []

    for name, price, stock in product_specs:
        product = Product(
            name=f"{name} {unique_id}",
            price=price,
            category_id=category.id,
        )
        db.add(product)
        db.flush()

        inventory = Inventory(
            product_id=product.id,
            total_quantity=stock,
            reserved_quantity=0,
        )
        db.add(inventory)

        products.append(
            {
                "product": product,
                "inventory": inventory,
                "stock": stock,
            }
        )

    db.commit()

    service = OrderService(
        order_repository=OrderRepository(db),
        customer_repository=CustomerRepository(db),
        product_repository=ProductRepository(db),
        inventory_repository=InventoryRepository(db),
        order_item_repository=OrderItemRepository(db),
    )

    return {
        "customer": customer,
        "user": user,
        "products": products,
        "service": service,
    }


def test_create_order_success_with_multiple_products():
    db = TestSessionLocal()

    try:
        context = _create_order_context(
            db,
            [
                ("Keyboard", Decimal("100.00"), 10),
                ("Mouse", Decimal("50.00"), 8),
            ],
        )

        keyboard = context["products"][0]
        mouse = context["products"][1]

        order_data = OrderCreate(
            items=[
                OrderItemCreate(
                    product_id=keyboard["product"].id,
                    quantity=2,
                ),
                OrderItemCreate(
                    product_id=mouse["product"].id,
                    quantity=3,
                ),
            ]
        )

        order = context["service"].create_order(
            customer_id=context["customer"].id,
            order_data=order_data,
            current_user=context["user"],
        )

        db.expire_all()

        saved_order = db.get(Order, order.id)

        assert saved_order is not None
        assert saved_order.customer_id == context["customer"].id
        assert saved_order.total_amount == Decimal("350.00")
        assert saved_order.reservation_until is not None

        saved_keyboard_inventory = db.get(
            Inventory, keyboard["inventory"].id
        )
        saved_mouse_inventory = db.get(
            Inventory, mouse["inventory"].id
        )

        assert saved_keyboard_inventory.reserved_quantity == 2
        assert saved_keyboard_inventory.available_quantity == 8

        assert saved_mouse_inventory.reserved_quantity == 3
        assert saved_mouse_inventory.available_quantity == 5

        order_items = (
            db.query(OrderItem)
            .filter(OrderItem.order_id == order.id)
            .all()
        )

        assert len(order_items) == 2

        actual_items = {
            item.product_id: (item.quantity, item.unit_price)
            for item in order_items
        }

        assert actual_items[keyboard["product"].id] == (
            2, Decimal("100.00")
        )
        assert actual_items[mouse["product"].id] == (
            3, Decimal("50.00")
        )

    finally:
        db.rollback()
        db.close()


def test_create_order_rolls_back_when_later_product_has_insufficient_stock():
    db = TestSessionLocal()

    try:
        context = _create_order_context(
            db,
            [
                ("Available Product", Decimal("100.00"), 10),
                ("Limited Product", Decimal("50.00"), 1),
            ],
        )

        first_product = context["products"][0]
        second_product = context["products"][1]

        order_data = OrderCreate(
            items=[
                OrderItemCreate(
                    product_id=first_product["product"].id,
                    quantity=2,
                ),
                OrderItemCreate(
                    product_id=second_product["product"].id,
                    quantity=2,
                ),
            ]
        )

        with pytest.raises(InsufficientInventoryError):
            context["service"].create_order(
                customer_id=context["customer"].id,
                order_data=order_data,
                current_user=context["user"],
            )

        db.expire_all()

        # Pehle product ki reservation bhi rollback honi chahiye.
        first_inventory = db.get(
            Inventory, first_product["inventory"].id
        )
        second_inventory = db.get(
            Inventory, second_product["inventory"].id
        )

        assert first_inventory.reserved_quantity == 0
        assert first_inventory.available_quantity == 10

        assert second_inventory.reserved_quantity == 0
        assert second_inventory.available_quantity == 1

        order_count = (
            db.query(Order)
            .filter(
                Order.customer_id == context["customer"].id
            )
            .count()
        )
        assert order_count == 0

        order_item_count = (
            db.query(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(
                Order.customer_id == context["customer"].id
            )
            .count()
        )
        assert order_item_count == 0

    finally:
        db.rollback()
        db.close()


def test_create_order_rolls_back_when_product_does_not_exist():
    db = TestSessionLocal()

    try:
        context = _create_order_context(
            db,
            [
                ("Existing Product", Decimal("100.00"), 10),
            ],
        )

        # Existing product ko pehle request mein process karna hai.
        existing_product = context["products"][0]["product"]

        # IDs are positive auto-increment values; this ID should be absent.
        missing_product_id = 2_000_000_000

        assert db.get(Product, missing_product_id) is None

        order_data = OrderCreate(
            items=[
                OrderItemCreate(
                    product_id=existing_product.id,
                    quantity=2,
                ),
                OrderItemCreate(
                    product_id=missing_product_id,
                    quantity=1,
                ),
            ]
        )

        with pytest.raises(ProductNotFoundError):
            context["service"].create_order(
                customer_id=context["customer"].id,
                order_data=order_data,
                current_user=context["user"],
            )

        db.expire_all()

        inventory = db.get(
            Inventory,
            context["products"][0]["inventory"].id,
        )

        assert inventory.reserved_quantity == 0
        assert inventory.available_quantity == 10

        order_count = (
            db.query(Order)
            .filter(
                Order.customer_id == context["customer"].id
            )
            .count()
        )
        assert order_count == 0

        order_item_count = (
            db.query(OrderItem)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(
                Order.customer_id == context["customer"].id
            )
            .count()
        )
        assert order_item_count == 0

    finally:
        db.rollback()
        db.close()
