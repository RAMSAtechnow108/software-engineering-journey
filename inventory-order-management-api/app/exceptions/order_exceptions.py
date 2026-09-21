from app.exceptions.app_exception import AppException
from fastapi import status


class OrderNotFoundError(AppException):

    def __init__(self, order_id):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Order not found with {order_id}",
            error_code="ORDER_NOT_FOUND"
        )


class InvalidOrderStatusTransitionError(AppException):

    def __init__(self, current_status, new_status):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=(
                f"Invalid order status transition "
                f"from '{current_status}' to '{new_status}'"
            ),
            error_code="INVALID_ORDER_STATUS_TRANSITION"
        )