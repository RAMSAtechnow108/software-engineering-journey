from app.exceptions.app_exception import AppException
from fastapi import status

class OrderNotFoundError(AppException):
    
    def __init__(self, order_id):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Order not found with {order_id}",
            error_code="ORDER_NOT_FOUND"
        )