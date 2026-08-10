import logging

from app.schemas.inventory_schema import InventoryUpdate


logger = logging.getLogger(__name__)


class InventoryService:
    
    def __init__(self, repository):
        self.repository = repository
        
        
    def get_inventory_by_product_id(self, product_id:int):
        
        logger.info("Getting inventory for product_id=%s",product_id)
        
        inventory = self.repository.get_inventory_by_product_id(product_id)
        
        logger.info("Inventory fetched successfully for product_id=%s",product_id)

        return inventory

    
    def update_inventory(self,product_id:int, inventory_data:InventoryUpdate):
        
        logger.info("Updating inventory with product_id=%s",product_id)

        inventory = self.repository.update_inventory(product_id,inventory_data)

        logger.info("Inventory update successfully by product_id=%s",product_id)

        return inventory