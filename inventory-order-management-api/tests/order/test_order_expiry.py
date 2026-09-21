from datetime import datetime,timedelta
from decimal import Decimal

from sqlalchemy import select

from tests.database import TestSessionLocal
from app.repositories.order_repository import OrderRepository
from app.models.customer import Customer
from app.models.order import Order
from app.models.category import Category
from app.models.inventory import Inventory
from app.models.order_item import OrderItem
from app.models.product import Product

from app.constants. order_constants import OrderStatus 


from app.services.order_service import OrderService

from app.repositories.customer_repository import CustomerRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_item_repository import OrderItemRepository

def test_get_expired_orders():
    
    db = TestSessionLocal()

    try:
        repository = OrderRepository(db)
        
        customer = Customer(
            name="Test Customer",
            email="test@example.com",
            phone="234432123"
        )

        db.add(customer)
        db.flush()
        
        
        current_time = datetime.now()

        expired_order =Order(
            order_number = "TEST-EXPIRED-001",
            customer_id = customer.id,
            status = OrderStatus.PENDING,
            total_amount = 0,
            reservation_until = current_time - timedelta(minutes=1)
        )
        
        db.add(expired_order)
        
        future_order = Order(
            order_number="TEST-FUTURE-001",
            customer_id=customer.id,
            status=OrderStatus.PENDING,
            total_amount=0,
            reservation_until=current_time + timedelta(minutes=10)
        )
        db.add(future_order)
        

        
        confirmed_order = Order(
            order_number = "TEST-CONFIRMED-001",
            customer_id = customer.id,
            status = OrderStatus.CONFIRMED,
            total_amount = 0,
            reservation_until =current_time
        )
        
        db.add(confirmed_order)
        db.flush()
        
        expired_orders = repository.get_expired_orders(current_time)
        
        assert len(expired_orders) == 1
        assert expired_orders[0].order_number == "TEST-EXPIRED-001"
        
        
        locked_order = repository.get_order_for_update(expired_order.id)

        assert locked_order is not None
        assert locked_order.id == expired_order.id
        
    finally:
        db.close()
        
        
def test_expire_order():
    
    db = TestSessionLocal()
    
    try:    
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
        
        
        customer = Customer(
            name = "Expiry Test Cusotmer",
            email = "expiry@gmail.com",
            phone = "9876543210"
        )
        
        
        db.add(customer)
        db.flush()
        
        
        
        category = Category(
            name = "Expiry Test Category"
        )
        
        db.add(category)
        db.flush()

        product = Product(
            name="Expiry Test Product",
            price=Decimal("100.00"),
            category_id=category.id
        )

        db.add(product)
        db.flush()
        
        
        inventory = Inventory(
            product_id = product.id,
            total_quantity = 10,
            reserved_quantity = 3
        )
        
        db.add(inventory)
        db.flush()
        
        current_time  = datetime.now()

        order = Order(
            order_number = "TEST-EXPIRY-ORDER-001",
            customer_id = customer.id,
            status = OrderStatus.PENDING,
            total_amount = Decimal("300.00"),
            reservation_until = current_time-timedelta(minutes=1)
        )
        
        db.add(order)
        db.flush()
        
        
        order_item = OrderItem(
            order_id = order.id,
            product_id = product.id,
            product_name = product.name,
            quantity = 3,
            unit_price =product.price
        )
        
        db.add(order_item)
        db.flush()
        
        
        service.expire_orders(current_time)

        
        db.refresh(order)
        db.refresh(inventory)
        
        assert order.status == OrderStatus.EXPIRED
        assert inventory.reserved_quantity == 0
        assert inventory.total_quantity == 10
    
    finally:
        db.close()        
        
        

def test_expired_order_rollback():
    db = TestSessionLocal()

    try:
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
        
        
        
        customer = Customer(
            name = "Rollback Test Customer",
            email = "rollback@example.com",
            phone = "9876543211"
        )
        
        db.add(customer)
        db.flush()

        
        category = Category(
            name = "Rollback Test Category"
        )
        
        db.add(category)
        db.flush()

        
        product_a = Product(
            name ="Rollback Proudct A",
            price = Decimal("100.00"),
            category_id = category.id
        )
        db.add(product_a)
        db.flush()


        product_b = Product(
            name  = "Rollback Product B",
            price = Decimal("200.00"),
            category_id = category.id
        )

        db.add(product_b)
        db.flush()
        
        inventory_a = Inventory(
            product_id = product_a.id,
            total_quantity = 10,
            reserved_quantity=2
        )
        
        db.add(inventory_a)
        db.flush()
        
        
        inventory_b = Inventory(
            product_id = product_b.id,
            total_quantity = 10,
            reserved_quantity = 1
        )
        db.add(inventory_b)
        db.flush()
        
        current_time = datetime.now()


        order = Order(
            order_number = "TEST-ROLLBACK-ORDER-001",
            customer_id = customer.id,
            status = OrderStatus.PENDING,
            total_amount = Decimal("800.00"),
            reservation_until = current_time-timedelta(minutes=1)
        )

        db.add(order)
        db.flush()
        
        
        order_item_a = OrderItem(
            order_id = order.id,
            product_id = product_a.id,
            product_name = product_a.name,
            quantity = 2,
            unit_price = product_a.price
        )
        
        db.add(order_item_a)
        db.flush()

        order_item_b = OrderItem(
            order_id=order.id,
            product_id=product_b.id,
            product_name=product_b.name,
            quantity=3,
            unit_price=product_b.price
        )

        db.add(order_item_b)
        db.flush()
        db.commit()
        
        import pytest


        with pytest.raises(ValueError):
            service.expire_orders(current_time)
        
        
        inventory_a_after = db.execute(
            select(Inventory).where(
                Inventory.product_id== product_a.id
            )
        ).scalar_one()
        
        
        inventory_b_after = db.execute(
            select(Inventory).where(
                Inventory.product_id== product_b.id
            )
        ).scalar_one()
        
        order_after = db.execute(
            select(Order).where(Order.id==order.id)
        ).scalar_one()
            
            
        assert order_after.status == OrderStatus.PENDING
        assert order.status == OrderStatus.PENDING
        assert inventory_a.reserved_quantity == 2
        assert inventory_b.reserved_quantity == 1
        
        
    finally:
        db.close()