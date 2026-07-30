from app.schemas.product_schema import ProductCreate,ProductUpdate
import logging
from app.constants.product_constants import PRODUCT_SORT_FIELDS,SORT_ORDER
from app.exceptions.product_exceptions import InvalidOrderFieldError, InvalidSortFieldError,InvalidPriceRangeError


logger = logging.getLogger(__name__)


class ProductService:
    
    
    def __init__(self, repository):
        self.repository = repository
        

    def get_products(self, page: int, limit: int,sort_by: str, order: str,category_id:int, min_price: float, max_price:float,search: str):
        
        
        if sort_by not in PRODUCT_SORT_FIELDS:
            raise InvalidSortFieldError(sort_by)
        
        if order not in SORT_ORDER:
            raise InvalidOrderFieldError(order)
        
        if min_price is not None and max_price is not None:
            if min_price>max_price:
                raise InvalidPriceRangeError()
        
        if search is not None:
            search = search.strip()
            if not search:
                search=None
                
        offset = (page-1)*limit

        column =   PRODUCT_SORT_FIELDS[sort_by]
        
        if order == "desc":
            column = column.desc()
        else:
            column=column.asc()
        
        logger.info("Getting products for page=%s, limit=%s",page,limit)
        
        products = self.repository.get_products(offset, limit, column,category_id,min_price,max_price, search)
        
        logger.info("Retrieved %s products", len(products))
        
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
        