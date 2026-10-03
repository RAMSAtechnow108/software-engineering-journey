import logging

from app.exceptions.auth_exceptions import InvalidCredentialsError
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import LoginRequest
from app.security.password import verify_password

from app.security.jwt import create_access_token



logger = logging.getLogger(__name__)



class AuthService:
    
    def __init__(self,user_repository:UserRepository):
        self.user_repository = user_repository
        
        
    def authenticate_user(self, login_data:LoginRequest):
        logger.info(
            "Authentication attempt for email=%s", login_data.email
        )
        
        user = self.user_repository.get_user_by_email(login_data.email)

        if user is None:
            raise InvalidCredentialsError()

        if not verify_password(login_data.password, user.password_hash):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InvalidCredentialsError()

        logger.info("User authentication successfull, user_id=%s",user.id)
        
        access_token = create_access_token(user_id=user.id, role=user.role.value)

        return access_token