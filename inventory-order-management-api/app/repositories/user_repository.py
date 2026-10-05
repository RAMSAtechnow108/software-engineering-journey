import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.constants.user_constants import UserRole
from app.exceptions.user_exceptions import DuplicateUserEmailError


logger = logging.getLogger(__name__)


class UserRepository:
    
    def __init__(self, db:Session):
        self.db = db 
        
    def get_user_by_email(self, email:str) -> User | None:
        
        logger.info("Getting user by email")

        statement = select(User).where(User.email==email)

        result = self.db.execute(statement)

        user = result.scalar_one_or_none()

        return user
    
    
    def create_user(self, email: str, password_hash: str, customer_id: str) -> User:
        
        logger.info("Creating user account")

        new_user = User(
            email = email,
            password_hash= password_hash,
            customer_id=customer_id
        )
        
        
        self.db.add(new_user)
        
        try:
            
            self.db.flush()

        except IntegrityError as exc:
            logger.exception("Duplicate user email detected fro email=%s", email)
            
            raise DuplicateUserEmailError(email) from exc
        logger.info("User added to transaction with user_id=%s",new_user.id)

        return new_user
        
    
    
    def get_user_by_id(self, user_id:int) ->User|None:
        logger.info("Getting user be user_id=%s", user_id)

        statement  = select(User).where(User.id == user_id)

        result = self.db.execute(statement)
        return result.scalar_one_or_none()
    
    
    
    def create_admin_user(self, email:str, password_hash: str) -> User:
        
        logger.info("Creating admin user with email=%s", email)

        new_user = User(
            email=email, password_hash=password_hash, role=UserRole.ADMIN, customer_id=None
        )
        
        self.db.add(new_user)

        try:
            self.db.flush()

        except IntegrityError as exc:
            logger.exception("Admin user creation failed for email=%s", email)

            raise DuplicateUserEmailError(email) from exc
        logger.info("Admin user added to transaction with user_id=%s", new_user.id)

        return new_user
    
    
    
    
    def get_all_users(self) -> list[User]:
        logger.info("Getting all users")
        statement = select(User).order_by(User.id)
        result = self.db.execute(statement)
        return result.scalars().all()