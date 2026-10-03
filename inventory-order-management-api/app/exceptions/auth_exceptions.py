from fastapi import status
from app.exceptions.app_exception import AppException

class InvalidCredentialsError(AppException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid email or password",
            error_code="INVALID_CREDENTIALS"
        )
        
        