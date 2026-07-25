from app.schemas.product_schema import ProductCreate,ProductUpdate
from app.exceptions.product_exceptions import ProductNotFoundError
from sqlalchemy.orm import Session
from app.models.product import Product
from sqlalchemy import select
import logging



logger = logging.getLogger(__name__)



class ProductRepository:
    def __init__(self,db:Session):
        self.db = db
        
        
        
    def get_products(self):
       
        logger.info("Fetching all products from database")
        return self.db.execute(select(Product)).scalars().all()



    def get_product(self,id:int):
        
        logger.info(f"Fetching product with ID {id}")
        
        stmt = select(Product).where(Product.id == id)
        product = self.db.execute(stmt).scalar_one_or_none()
                
        if product is None:
            logger.warning(f"Product not found with ID {id}")
            raise ProductNotFoundError(id)
        
        logger.info(f"Product found with ID {id}")

        return product
    
    
    
    def create_product(self,product: ProductCreate):
        
        logger.info("Creating new product")
        
        logger.debug(f"Product Data -> Name: {product.name}, Price: {product.price}, Quantity: {product.quantity}")
        
        try:
            
            new_product = Product(
                        name = product.name,
                        price=product.price, 
                        quantity=product.quantity
                    )
            
            self.db.add(new_product)
            self.db.commit()
            self.db.refresh(new_product)
            
            logger.info(f"Product created successfully with ID {new_product.id}")
            return new_product
        
        except Exception:
            self.db.rollback()
            logger.exception("Database error while creating product")
            raise
        
    
    def update_product(self, id:int,product:ProductUpdate):
        
        logger.info(f"Updating product with ID {id}")
        
        existing_product = self.get_product(id)
        
        try:
            
            logger.debug("Applying request field updates")
            
            if product.name is not None:
                existing_product.name = product.name
            if product.price is not None:
                existing_product.price = product.price
            if product.quantity is not None:
                existing_product.quantity = product.quantity
            
            logger.debug("Field updates applied successfully")
            
            logger.debug("Committing changes to database")

            self.db.commit()


            logger.debug(f"Refreshing product {id} from database")

            self.db.refresh(existing_product)
            
            logger.info(f"Product {id} updated successfully")

            return existing_product
        
        except Exception:
            self.db.rollback()
            logger.exception("Database error while updateting product")
            raise
        
    
    def delete_product(self,id:int):
        
        logger.info(f"Deleting record with ID {id}")
        
        try:
            
            existing_product = self.get_product(id)
            
            logger.debug(f"Product found. Deleting product with ID {id}")
            self.db.delete(existing_product)
            
            logger.debug("Committing delete transaction")
            self.db.commit()
            
            logger.info(f"Product with ID {id} deleted successfully")
        except Exception:
            self.db.rollback()
            logger.exception(f"Database error while deleting product with ID {id}")            
            raise
        
            
        