from app.schemas.product_schema import ProductCreate,ProductUpdate
import logging


logger = logging.getLogger(__name__)


class ProductService:
    
    
    def __init__(self, repository):
        self.repository = repository

    def get_products(self):
        logger.info("Getting all products")
        products = self.repository.get_products()
        logger.info("Product retrieved successfully")
        return products

    def get_product(self,id:int):
        logger.info(f"Getting product with ID {id}")
        product =  self.repository.get_product(id)
        logger.info(f"Getting product with ID {id} successfully")
        return product
        
    def create_product(self, product):
        logger.info("Creating product")

        new_product = self.repository.create_product(product)

        logger.info("Product created successfully")

        return new_product
    
    def update_product(self,id: int, product:ProductUpdate):
        logger.info(f"Updating product with ID {id}")
        update_product = self.repository.update_product(id,product)
        logger.info(f"Product with ID {id} updated successfully")
        return update_product
    
    
    def delete_product(self,id:int):
        logger.info(f"Deleting product with ID {id}")
        result =  self.repository.delete_product(id)
        logger.info(f"Product with ID {id} updated successfully")
        return result
        