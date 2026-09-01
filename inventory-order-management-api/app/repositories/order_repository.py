from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal

from uuid import uuid4
from datetime import datetime

from app.models.order import Order
from app.models.order_item import OrderItem
from app.exceptions.order_exceptions import OrderNotFoundError
from app.constants.order_constants import OrderStatus

import logging


logger = logging.getLogger(__name__)

class OrderRepository:
    
    def __init__(self, db:Session):
        self.db = db
        
    
    def get_order_by_id(self, order_id:int):
        
        try:
            logger.info("Getting order with order_id=%s",order_id)

            result = self.db.execute(select(Order).where(Order.id == order_id))
            
            order = result.scalar_one_or_none()

            if order is None:
                logger.warning("Order is not found with order_id=%s",order_id)
                raise OrderNotFoundError(order_id)
            
            logger.info("Order fetch successfully with order_id=%s",order_id)

            return order
        
        except OrderNotFoundError:
            raise
        
        except SQLAlchemyError:
            logger.exception("Database error while fetching order")
            raise

        except Exception:
            logger.exception("Unexpected error while fetching order with order_id%s", order_id)
            raise
        
    def create_order(self, customer_id: int,reservation_until:datetime):
        
        logger.info("Creating order for customer_id=%s", customer_id)

        try:
            
            order_number = f"ORD-{uuid4().hex[:8].upper()}"
            
            new_order = Order(
                order_number=order_number,
                customer_id = customer_id,
                status = OrderStatus.PENDING,
                total_amount = Decimal("0.00"),
                reservation_until = reservation_until
            )
            
            self.db.add(new_order)

            logger.debug("Order added to session for customer_id=%s",customer_id)
 
            self.db.flush()

            logger.info("Order created in transaction with order_id=%s, order_number=%s", new_order.id, new_order.order_number)

            return new_order
        
        except SQLAlchemyError:
            logger.exception(
                "Database error while creating order for customer_id=%s", customer_id
            )
            raise
        
        except Exception:
            logger.exception(
                "Unexcepted error while creating order for customer_id=%s", customer_id
            )