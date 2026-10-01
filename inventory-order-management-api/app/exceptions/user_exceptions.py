from app.exceptions.app_exception import AppException
from fastapi import status

class DuplicateUserEmailError(AppException):
    
    def __init__(self, email:str):
        super().__init__(
            message=f"User with email {email} already exists",
            status_code=status.HTTP_409_CONFLICT,
            error_code="DUPLICATE_USER_EMAIL"
            )