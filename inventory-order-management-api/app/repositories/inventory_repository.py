from sqlalchemy.orm import Session
from sqlalchemy import select
import logging
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.inventory_schema import InventoryUpdate



from app.models.inventory import Inventory

from app.exceptions.inventory_exceptions import InventoryNotFoundError, InsufficientInventoryError


logger = logging.getLogger(__name__)

class InventoryRepository:
    
    def __init__(self, db:Session):
        self.db  = db
        
    
    def get_inventory_by_product_id(self,product_id:int):
        
        try:
            logger.info("Getting inventory of product with product_id=%s",product_id)
            
            result = self.db.execute(
                select(Inventory).where(
                    Inventory.product_id==product_id
                )
            )

            inventory = result.scalar_one_or_none()

            if inventory is None:
                logger.warning("Inventory not found from product_id=%s",product_id)
                raise InventoryNotFoundError(product_id)
            
            logger.info("Inventory fetched successfully for product_id=%s",product_id)

            return inventory
        except InventoryNotFoundError:
            raise
        
        except SQLAlchemyError:
            logger.exception("Database error while getting iventory for product id=%s",product_id)
            raise
        
        except Exception:
            logger.exception("Unexpected error while getting product inventory with id=%s",product_id)
            raise
    
    
    def update_inventory(self, product_id:int, inventory_data: InventoryUpdate):
        
        logger.info("Updating inventory with product_id %s",product_id)
        
        try:
            
            inventory = self.get_inventory_by_product_id(product_id)
            
            logger.debug("Applying request field updates")

            inventory.total_quantity = inventory_data.total_quantity
            
            logger.debug("Field updates applied successfully.")

            logger.debug("Committing changes to database")
            
            self.db.commit()
            
            self.db.refresh(inventory)
            
            logger.info("Inventory for product_id=%s updated successfully",product_id)

            return inventory
        
        except InventoryNotFoundError:
            raise
        
        except SQLAlchemyError:
            self.db.rollback()
            logger.exception(
                "Database error while updating inventory")
            raise

        except Exception:
            self.db.rollback()
            logger.exception("Database error while updating inventory")
            raise
            

    def reserve_stock(self, product_id: int, quantity: int):

        logger.info(
            "Starting stock reservation: product_id=%s, requested_quantity=%s",
            product_id,
            quantity
        )

        try:

            inventory = self.get_inventory_by_product_id(product_id)

            available_quantity = inventory.available_quantity

            if available_quantity < quantity:

                logger.warning(
                    "Insufficient inventory: product_id=%s, requested=%s, available=%s",
                    product_id,
                    quantity,
                    available_quantity
                )

                raise InsufficientInventoryError(
                    product_id=product_id,
                    requested_quantity=quantity,
                    available_quantity=available_quantity
                )

            old_reserved = inventory.reserved_quantity

            inventory.reserved_quantity += quantity

            logger.info(
                "Stock reserved successfully: product_id=%s, old_reserved=%s, new_reserved=%s",
                product_id,
                old_reserved,
                inventory.reserved_quantity
            )

            return inventory

        except InsufficientInventoryError:
            raise

        except SQLAlchemyError:
            logger.exception(
                "Database error while reserving stock: "
                "product_id=%s, quantity=%s",
                product_id,
                quantity
            )
            raise

        except Exception:
            logger.exception(
                "Unexpected error while reserving stock: "
                "product_id=%s, quantity=%s",
                product_id,
                quantity
            )
            raise