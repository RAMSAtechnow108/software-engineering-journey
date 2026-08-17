from sqlalchemy.orm import Session
from sqlalchemy import select
import logging
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


from app.models.customer import Customer

from app.schemas.customer_schema import CustomerCreate,CustomerUpdate
from app.exceptions.customer_exceptions import CustomerNotFoundError, DuplicateCustomerEmailError,DuplicateCustomerPhoneError
logger =logging.getLogger(__name__)


class CustomerRepository:
    
    def __init__(self, db: Session):
        self.db = db
        
    
    def get_customer_by_id(self, customer_id: int):

        try:
            
            logger.info("Getting customer with customer_id=%s",customer_id)

            result = self.db.execute(select(Customer).where(Customer.id==customer_id))
            
            customer = result.scalar_one_or_none()

            if customer is None:
                logger.warning("Customer not found with cusotmer_id=%s",customer_id)
                raise CustomerNotFoundError(customer_id)
            
            logger.info("Customer fetch successfully with customer_id=%s",customer_id)

            return customer
        
        except CustomerNotFoundError:
            raise
        
        
        except SQLAlchemyError:
            logger.exception("Database error while getting customer with customer_id=%s",customer_id)
            raise
        
        except Exception:
            logger.exception("Unexpected error occuring while getting customer with customer_id=%s",customer_id)
            raise
        
    
    def create_customer(self, customer_data: CustomerCreate):

        logger.info("Creating customer with name=%s",customer_data.name)        
        try: 
            
            logger.debug("Customer object created with name=%s, email=%s",customer_data.name, customer_data.email)
            
            existing_email = self.db.execute(select(Customer).where(Customer.email == customer_data.email)).scalar_one_or_none()

            if existing_email:
                raise DuplicateCustomerEmailError(customer_data.email)

            existing_phone = self.db.execute(select(Customer).where(Customer.phone == customer_data.phone)).scalar_one_or_none()

            if existing_phone:
                raise DuplicateCustomerPhoneError(customer_data.phone)

            
            new_customer = Customer(
                name=customer_data.name,
                email=customer_data.email,
                phone=customer_data.phone
            )
            
            self.db.add(new_customer)
            
            logger.debug("Customer added to database session with email=%s",customer_data.email)

            self.db.commit()
            
            logger.info("Customer created successfully with customer_id=%s",new_customer.id)
            
            self.db.refresh(new_customer)

            logger.debug("Customer refreshed successfully with customer_id=%s",new_customer.id)

            return new_customer
        
        except (DuplicateCustomerEmailError,DuplicateCustomerPhoneError):
            raise
        
        except IntegrityError as exc:
            self.db.rollback()
            
            constraint_name = str(exc.orig)

            if "uq_customers_email" in constraint_name:
                logger.warning("Duplicate Customer email attempted: email=%s",customer_data.email)
                raise DuplicateCustomerEmailError(customer_data.email) from exc
            
            if "uq_customers_phone" in constraint_name:
                logger.warning("Duplicate customer phone attempted: phone=%s",customer_data.phone)
                raise DuplicateCustomerPhoneError(customer_data.phone) from exc
            
            logger.exception("Unexpected Integrity error while creating customer.")

            raise
        
        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Database error while creating customer.")
            raise
        
        except Exception:
            self.db.rollback()
            logger.exception("Unexpected error while creating customer.")
            raise
            
            
            
    def update_customer(self, customer_id:int, customer_data: CustomerUpdate):
        
        logger.info("Updating customer with customer_id=%s",customer_id)
        
        existing_customer = self.get_customer_by_id(customer_id)
        
        try:
            
            logger.debug("Applying request field updates")

            existing_customer.name = customer_data.name
            
            logger.debug("Field updates applied successfully")

            logger.debug("Committing changes to database")

            self.db.commit()

            logger.debug("Refreshing customer_id=%s", customer_id)

            self.db.refresh(existing_customer)

            logger.info("Customer_id=%s updated successfully", customer_id)

            return existing_customer
        
        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Database error while updating customer")
            raise
        
        except Exception:
            logger.exception("Unexpected Error while updating customer.")
            raise


          