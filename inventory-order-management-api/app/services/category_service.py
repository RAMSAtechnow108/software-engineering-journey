import logging
from app.constants.category_constants import SORT_ORDER,CATEGORY_SORT_FIELDS
from app.exceptions.category_exceptions import InvalidOrderFieldError,InvalidSortFieldError

logger = logging.getLogger(__name__)

class CategoryService:
    
    def __init__(self,repository):
        self.repository = repository
        
    
    
    def get_all_categories(self,page:int, limit:int, sort_by:int, order, category_name:str):
        
        logger.info(
                    "Fetching categories | page=%s, limit=%s, sort_by=%s, order=%s, category_name=%s",
                    page,
                    limit,
                    sort_by,
                    order,
                    category_name,
        )        
        if sort_by not in CATEGORY_SORT_FIELDS:
            logger.warning("Invalid sort field: %s", sort_by)
            raise InvalidSortFieldError(sort_by)
        
        if order not in SORT_ORDER:
            logger.warning("Invalid order: %s",order)
            raise InvalidOrderFieldError(order)
        
        column =    CATEGORY_SORT_FIELDS[sort_by]
        
        if order=="desc":
            column = column.desc()
        else:
            column = column.asc()
        
        offset = (page - 1) * limit
        
        categories =  self.repository.get_all_categories(offset,limit,column,category_name)
        
        logger.info("Retrieved %s categories",len(categories))
        return categories




    def get_category_by_id(self,category_id):
        logger.info("Fetching category with id=%s",category_id)
        return self.repository.get_category_by_id(category_id)


    def create_category(self,category):
        logger.info("Creating category %s",category.name)
        reslut = self.repository.create_category(category)
        logger.info("Category created successfully")
        return reslut
    
    def update_category(self,category_id,category):
        logger.info("Updating category id=%s",category_id)
        result = self.repository.update_category(category_id,category)
        logger.info("Category update successfull")
        return result
    
    
    def delete_category(self,category_id):
        logger.info("Deleting category id=%s",category_id)
        result = self.repository.delete_category(category_id)
        logger.info("Category deleted successfully")
        return result