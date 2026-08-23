import logging
from decimal import Decimal
from app.schemas.order_schema import OrderCreate


logger = logging.getLogger(__name__)


class OrderService:
    
    def __init__(
        self,
        order_repository,
        customer_repository,
        product_repository,
        inventory_repository,
        order_item_repository
    ):
        self.order_repository = order_repository
        self.customer_repository = customer_repository
        self.product_repository = product_repository
        self.inventory_repository = inventory_repository
        self.order_item_repository = order_item_repository
        
        
    
    def get_order_by_id(self, order_id:int):
        
        logger.info("Getting order witg order_id=%s",order_id)

        order = self.order_repository.get_order_by_id(order_id)

        logger.info("Order fetched successfully with order_id=%s",order_id)

        return order
    

    
    def create_order(self, customer_id:int, order_data:OrderCreate):
        
        logger.info("Creating order for customer_id=%s",customer_id)

        try:
            
            self.customer_repository.get_customer_by_id(customer_id)

            order = self.order_repository.create_order(customer_id)
            
            total_amount = Decimal("0.00")

            for item in order_data.items:
                
                product = self.product_repository.get_product_by_id(item.product_id)

                self.inventory_repository.reserve_stock(product_id=item.product_id, quantity=item.quantity)

                self.order_item_repository.create_order_item(
                    order_id = order.id,
                    product_id = product.id,
                    product_name = product.name,
                    quantity = item.quantity,
                    unit_price = product.price
                )
        
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
                    