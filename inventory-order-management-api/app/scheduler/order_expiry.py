from datetime import datetime
from app.core.database import SessionLocal

from app.repositories.order_repository import OrderRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_item_repository import OrderItemRepository

from app.services.order_service import OrderService

from apscheduler.schedulers.background import BackgroundScheduler

import logging


logger = logging.getLogger(__name__)


def expire_orders_job():
    
    db = SessionLocal()
    
    try:
        
        order_repository = OrderRepository(db)
        customer_repository = CustomerRepository(db)
        product_repository = ProductRepository(db)
        inventory_repository = InventoryRepository(db)
        order_item_repository = OrderItemRepository(db)

        service = OrderService(
            order_repository=order_repository,
            customer_repository=customer_repository,
            product_repository= product_repository,
            inventory_repository=inventory_repository,
            order_item_repository=order_item_repository
        )

        current_time = datetime.now()

        service.expire_orders(current_time)

    finally:
        db.close()


scheduler = BackgroundScheduler()

def start_scheduler():
        
    scheduler.add_job(expire_orders_job, "interval", minutes=1)

    scheduler.start()
    
    logger.info("Order expiry scheduler started")


def stop_scheduler():
    
    scheduler.shutdown()
    logger.info("Order expiry scheduler stopped")