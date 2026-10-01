import logging

from app.repositories.user_repository import UserRepository
from app.repositories.customer_repository import CustomerRepository

from app.schemas.user_schema import UserCreate
from app.schemas.customer_schema import CustomerCreate
from app.security.password import hash_password


logger = logging.getLogger(__name__)


class UserService:
    
    
    def __init__(self, user_repository: UserRepository, customer_repository: CustomerRepository):
        self.user_repository = user_repository
        self.customer_repository = customer_repository
        
        
    
    def register_customer(self, user_data:UserCreate):
        
        logger.info("Starting customer registration for email=%s", user_data.email)

        try:
        
            password_hash = hash_password(user_data.password)

            customer_data = CustomerCreate(
                name=user_data.name,
                email=user_data.email,
                phone=user_data.phone
            )
            
            
            customer = self.customer_repository.add_customer(customer_data)

            user = self.user_repository.create_user(
                email=user_data.email,
                password_hash=password_hash,
                customer_id=customer.id
            )        
            
            
            self.user_repository.db.commit()
            
            self.user_repository.db.refresh(user)
            self.customer_repository.db.refresh(customer)

            
            logger.info("Customer registration successful, user_id=%s, customer_id=%s", user.id, customer.id)


            return user, customer
    
        except Exception:
            self.user_repository.db.rollback()
            logger.exception("Customer registration failed for email_id=%s", user_data.email)

            raise
    