from app.exceptions.app_exception import AppException
from fastapi import status

class InventoryNotFoundError(AppException):
    
    def __init__(self,product_id):
        super().__init__(
            message=f"Inventory with id {product_id} is not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="INVENTORY_NOT_FOUND"
        )