from app.schemas.product_schema import ProductCreate,ProductUpdate
from app.exceptions.product_exceptions import ProductNotFoundError
from sqlalchemy.orm import Session
from app.models.product import Product
from sqlalchemy import select
import logging
from sqlalchemy.exc import SQLAlchemyError, IntegrityError



logger = logging.getLogger(__name__)



class ProductRepository:
    
    def __init__(self,db:Session):
        self.db = db
        
        
    def get_products(self, offset: int, limit: int, column, category_id:int, min_price: float, max_price:float, search :str):
        
        try:
            logger.info("Getting all products.")
            logger.info(
                "Getting products page=%s limit=%s category=%s search=%s",
                limit,
                offset,
                category_id,
                search,
            )
            query = select(Product)
            
            if category_id is not None:
                query = query.where(Product.category_id==category_id)
            
            if min_price is not None:
                query = query.where(Product.price >= min_price)
                
            if max_price is not None:
                query = query.where(Product.price <= max_price)
                
            if search is not None:
                query = query.where(Product.name.ilike(f"%{search}%"))
                
            query = query.order_by(column).offset(offset).limit(limit)

            result = self.db.execute(query)

            logger.info("Getting all products successfully")

            return result.scalars().all()
        
        except SQLAlchemyError :
            logger.exception("Database error while fetching categories.")

        except Exception:
            logger.exception('Unexpected error while fetching categories.')

    def get_product_by_id(self,product_id:int):
        
        try:
            logger.info("Fetching product with ID %s",product_id)
            
            stmt = select(Product).where(Product.id == product_id)
            product = self.db.execute(stmt).scalar_one_or_none()
                    
            if product is None:
                logger.warning("Product not found with ID %s",product_id)
                raise ProductNotFoundError(product_id)
            
            logger.info(f"Product found with ID %s",product_id)

            return product
        
        except SQLAlchemyError:
            logger.exception("Database error while fetching category.")
            raise
        
        except Exception:
            logger.exception("Unexpected error while fetching category.")
            raise
    
    
    def create_product(self,product: ProductCreate):
        
        logger.info("Creating new product")
        
        logger.debug(
            "Product Data -> Name: %s, Price: %s, Quantity: %s",
            product.name,
            product.price,
            product.quantity,
        )
                
        try:
            
            new_product = Product(
                        name = product.name,
                        price=product.price, 
                        quantity=product.quantity
                    )
            
            self.db.add(new_product)
            self.db.commit()
            self.db.refresh(new_product)
            
            logger.info("Product created successfully with ID %s",new_product.id)
            return new_product
        
        except Exception:
            self.db.rollback()
            logger.exception("Database error while creating product")
            raise
        
    
    def update_product(self, product_id:int,product:ProductUpdate):
        
        logger.info("Updating product with ID %s",product_id)
        
        existing_product = self.get_product(product_id)
        
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


            logger.debug("Refreshing product ID %s from database",product_id)

            self.db.refresh(existing_product)
            
            logger.info("Product ID %s updated successfully",product_id)

            return existing_product
        
        except Exception:
            self.db.rollback()
            logger.exception("Database error while updateting product")
            raise
        
    
    def delete_product(self,product_id:int):
        
        logger.info("Deleting record with ID %s",product_id)
        
        try:
            
            existing_product = self.get_product(product_id)
            
            logger.debug("Product found. Deleting product with ID %s", product_id)
            self.db.delete(existing_product)
            
            logger.debug("Committing delete transaction")
            self.db.commit()
            
            logger.info("Product with ID %s deleted successfully",product_id)
        except Exception:
            self.db.rollback()
            logger.exception("Database error while deleting product with ID %s",product_id)            
            raise   
        
            
        