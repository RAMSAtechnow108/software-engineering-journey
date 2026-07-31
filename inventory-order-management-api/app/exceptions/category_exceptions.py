from fastapi import status
from app.exceptions.app_exception import AppException

class CategoryNotFoundError(AppException):
    
    def __init__(self,category_id: int ):
        super().__init__(
            message=f"Category with ID {category_id} not found", 
            status_code=status.HTTP_404_NOT_FOUND, 
            error_code="CATEGORY_NOT_FOUND"
        )


class DuplicateCategoryError(AppException):
    
    def __init__(self,category_name: str):
        super().__init__(
            message=f"Category '{category_name}' already exists.",
            status_code=status.HTTP_409_CONFLICT,
            error_code="DUPLICATE_CATEGORY"
        )
        

class CategoryInUseError(AppException):
    
    def __init__(self, category_id:int):
        super().__init__(
            message=(f"Category with id{category_id} "
            "cannot be deleted because products are assigned to it."
            ),
            status_code=status.HTTP_409_CONFLICT,
            error_code="CATEGORY_IN_USE"
        )
        
class InvalidSortFieldError(AppException):
    
    def __init__(self, sort_by):
        super().__init__(
            message=f"Invalid sort field {sort_by}",
            status_code=status.HTTP_409_BAD_REQUEST,
            error_code="INVALID_SORT_ERROR"
        )
    


class InvalidOrderFieldError(AppException):
    
    def __init__(self, order:str):
        super().__init__(
            message=f"Invalid sort order: '{order}'. Allowed values are 'asc' and 'desc",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_SORT_ORDER"
        )
        