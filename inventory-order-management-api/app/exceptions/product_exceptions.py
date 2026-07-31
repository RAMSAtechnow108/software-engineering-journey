from app.exceptions.app_exception import AppException
from fastapi import status


class ProductNotFoundError(AppException):
    
    def __init__(self, product_id:int):
        super().__init__(
            message = f"Product with id {product_id} not found",
            status_code = status.HTTP_404_NOT_FOUND,
            error_code = "PRODUCT_NOT_FOUND"
        )


class DuplicateProductError(AppException):
    
    def __init__(self, product_name :str):
        super().__init__(
            message = f"Prduct '{product_name}' already exists.",
            status_code = status.HTTP_409_CONFLICT,
            error_code = "DUPLICATE_PRODUCT"
        )


class InvalidSortFieldError(AppException):
    
    def __init__(self, sort_by:str):
        super().__init__(
            message=f"Invalid sort field: {sort_by}",
            status_code= status.HTTP_400_BAD_REQUEST,
            error_code= "INVALID_SORT_FIELD"
        )
        

class InvalidOrderFieldError(AppException):
    
    def __init__(self, order:str):
        super().__init__(
            message=f"Invalid sort order: '{order}'. Allowed values are 'asc' and 'desc",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_SORT_ORDER"
        )
        
class InvalidPriceRangeError(AppException):
    
    def __init__(self):
        super().__init__(
            message="Minimum price cannot be greater than maximum price.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="INVALID_PRICE_RANGE"
        ) 
        