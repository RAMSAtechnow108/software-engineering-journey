from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.order_item import OrderItem

import logging

logger = logging.getLogger(__name__)


class OrderItemRepository:
    
    def __init__(self, db: Session):
        self.db = db
        
    
    def create_order_item(self, order_id:int, product_id:int, product_name:int, quantity:int, unit_price):
        
        logger.info("Creating   order item: order_id=%s, product_id=%s",order_id,product_id)

        try:
            
            new_order_item = OrderItem(
                order_id = order_id,
                product_id = product_id,
                product_name = product_name,
                quantity = quantity,
                unit_price = unit_price
            )
            
            self.db.add(new_order_item)

            self.db.flush()
            
            logger.info("Order item created with id=%s",new_order_item.id)

            return new_order_item
        
        except SQLAlchemyError:
            logger.exception("Database error while creating order item")
            raise
        
        except Exception:
            logger.exception("Unexpected error while creating order item")
            raise