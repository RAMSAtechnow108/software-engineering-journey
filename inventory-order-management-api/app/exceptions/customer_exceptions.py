from app.exceptions.app_exception import AppException
from fastapi import status


class CustomerNotFoundError(AppException):
    
    def __init__(self, customer_id: int ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Customer {customer_id} not found!",
            error_code="CUSTOMER_NOT_FOUND"
        )
    
    
class DuplicateCustomerEmailError(AppException):

    def __init__(self, email:str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=f"Customer {email} already exists",
            error_code="DUPLICATE_CUSTOMER_EMAIL"
        )

class DuplicateCustomerPhoneError(AppException):

    def __init__(self, phone:str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=f"Customer {phone} already exists",
            error_code="DUPLICATE_CUSTOMER_PHONE"
        )
