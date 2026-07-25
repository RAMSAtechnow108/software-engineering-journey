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
        return self.db.execute(select(Product)).scalars().all()



    def get_product(self,id:int):
        10/0
        stmt = select(Product).where(Product.id == id)
        product = self.db.execute(stmt).scalar_one_or_none()
                
        if product is None:
            raise ProductNotFoundError(id)
        
        return product
    
    
    
    def create_product(self,product: ProductCreate):
        
        new_product = Product(
            name = product.name,
            price=product.price, 
            quantity=product.quantity
        )
        
        self.db.add(new_product)
        self.db.commit()
        self.db.refresh(new_product)
        
        return new_product
        
    
    def update_product(self, id:int,product:ProductUpdate):
        existing_product = self.get_product(id)
        
        if product.name is not None:
            existing_product.name = product.name
        if product.price is not None:
            existing_product.price = product.price
        if product.quantity is not None:
            existing_product.quantity = product.quantity
            
        self.db.commit()
        self.db.refresh(existing_product)
        
        return existing_product
    
    
    def delete_product(self,id:int):
        existing_product = self.get_product(id)
        self.db.delete(existing_product)
        self.db.commit()
     
        
        