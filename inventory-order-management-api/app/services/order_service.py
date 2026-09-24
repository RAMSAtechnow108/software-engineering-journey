import logging
from decimal import Decimal
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.order_schema import OrderCreate
from app.constants.order_constants import OrderStatus
from app.domain.order_state.state_machine import OrderStateMachine
from app.exceptions.order_exceptions import OrderNotFoundError

from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OrderService:
    
    def __init__(
        self,
        order_repository,
        customer_repository,
        product_repository,
        inventory_repository,
        order_item_repository,
        order_state_machine = OrderStateMachine
    ):
        self.order_repository = order_repository
        self.customer_repository = customer_repository
        self.product_repository = product_repository
        self.inventory_repository = inventory_repository
        self.order_item_repository = order_item_repository
        self.order_state_machine = order_state_machine
        
        
    
    def get_order_by_id(self, order_id:int):
        
        logger.info("Getting order witg order_id=%s",order_id)

        order = self.order_repository.get_order_by_id(order_id)

        logger.info("Order fetched successfully with order_id=%s",order_id)

        return order
    

    
    def create_order(self, customer_id:int, order_data:OrderCreate):
        
        logger.info("Creating order for customer_id=%s",customer_id)

        try:
            
            self.customer_repository.get_customer_by_id(customer_id)
            
            reservation_until = datetime.now() + timedelta(minutes=15)
            
            order = self.order_repository.create_order(customer_id=customer_id, reservation_until=reservation_until)
            
            total_amount = Decimal("0.00")

            for item in order_data.items:
                
                product = self.product_repository.get_product_by_id(item.product_id)

                self.inventory_repository.reserve_stock(product_id=item.product_id, quantity=item.quantity)

                self.order_item_repository.create_order_item(order_id = order.id,product_id = product.id,product_name = product.name,quantity = item.quantity,unit_price = product.price)
        
                total_amount += (product.price * item.quantity)

            order.total_amount = total_amount

            self.order_repository.db.commit()
            self.order_repository.db.refresh(order)

            logger.info("Order created successfully: order_id=%s",order.id)

            return order

                
        except Exception:
            self.order_repository.db.rollback()

            logger.exception(
                "Error while creating order for customer_id=%s",
                customer_id
            )

            raise
    
    
    def expire_orders(self, current_time: datetime):
        
        logger.info("Starting expired order processing at=%s", current_time)

        try:
            
            expired_orders = self.order_repository.get_expired_orders(current_time)


            for expired_order in expired_orders:
                
                order = self.order_repository.get_order_for_update(expired_order.id)

                if order is None:
                    continue
                
                if order.status != OrderStatus.PENDING:
                    continue
                
                if order.reservation_until >current_time:
                    continue
                
                order_items = self.order_item_repository.get_order_items(order.id)

                for item in order_items:
                    
                    inventory = self.inventory_repository.get_inventory_for_update(item.product_id)
                    
                    if inventory.reserved_quantity<item.quantity:
                        raise ValueError(f"Insuficient reserved quantity for product_id={item.product_id}")
                        
                    inventory.reserved_quantity -= item.quantity

                self.order_state_machine.validate_transition(
                    order.status, OrderStatus.EXPIRED
                )
                
                order.status = OrderStatus.EXPIRED
                
            self.order_repository.db.commit()
                
            logger.info("Expired orders processed successfully")
        
        except SQLAlchemyError:
            self.order_repository.db.rollback()
            logger.exception("Database error while expiring orders")
            raise

        except Exception:
            
            self.order_repository.db.rollback()

            logger.exception("Error while expiring orders")
            raise


    def update_order_status(self, order_id:int, new_status:OrderStatus):
        
        logger.info("Updating order status, order_id=%s, new_status=%s", order_id, new_status)
        
        try:
            
            order = self.order_repository.get_order_by_id(order_id)
            
            self.order_state_machine.validate_transition(order.status, new_status)
            
            update_order = self.order_repository.update_order_status(order=order,new_status=new_status)

            self.order_repository.db.commit()
            self.order_repository.db.refresh(update_order)

            logger.info("Order status updated successfully, order_id=%s, new_status=%s", order_id, new_status)

            return update_order

        except SQLAlchemyError:
            self.order_repository.db.rollback()
            logger.exception("Database error while updating order status of order_id=%s", order_id)
            raise
        
        except Exception:
            self.order_repository.db.rollback()
            logger.exception("Unexpected error while updating order status of order_id=%s", order_id)
            raise
        
    
    def cancel_order(self, order_id:int):
        logger.info("Cancelling order, order_id=$s",order_id)

        try:
            order = self.order_repository.get_order_for_update(order_id)

            if order is None:
                raise OrderNotFoundError(order_id)
            
            
            self.order_state_machine.validate_transition(order.status,OrderStatus.CANCELLED)
            
            logger.info("Order cancellation validated,order_id=%s",order_id)
            
            order_item = self.order_item_repository.get_order_items(order.id)

            for item in order_item:
                inventory = self.inventory_repository.get_inventory_for_update(item.product_id)

                if inventory.reserved_quantity<item.quantity:
                    raise ValueError(
                        f"Insufficient reserved quantity "
                        f"for product_id={item.product_id}"
                    )
                    
                inventory.reserved_quantity -= item.quantity
                
            order.status = OrderStatus.CANCELLED
            
            self.order_repository.db.commit()
             

            return order

        except SQLAlchemyError:
            self.order_repository.db.rollback()
            logger.exception("Database error while cancelling order, order_id=%s", order_id)
            raise
        
        except Exception:
            self.order_repository.db.rollback()
            logger.exception("Error while cancelling order, order_id=%s", order_id)

            raise