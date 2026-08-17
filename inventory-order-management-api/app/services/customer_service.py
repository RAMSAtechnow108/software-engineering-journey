import logging
from app.schemas.customer_schema import CustomerCreate, CustomerUpdate


logger = logging.getLogger(__name__)

class CustomerService:
    
    def __init__(self,repository):
        self.repository = repository
        
    
    def get_customer_by_id(self,customer_id:int):
        
        logger.info("Getting customer with customer_id=%s",customer_id)

        customer = self.repository.get_customer_by_id(customer_id)

        logger.info("Customer fetched successfully with customer_id=%s",customer_id)

        return customer
    
    
    def create_customer(self, customer_data: CustomerCreate):
        
        logger.info("Creating customer")

        new_customer = self.repository.create_customer(customer_data)
        
        logger.info("Customer created successfully with customer_data=%s",new_customer.id)

        return new_customer
    
    
    def update_customer(self, customer_id:int, customer_data:CustomerUpdate):
        
        logger.info("Updating customer with customer_id=%s", customer_id)

        existing_customer = self.repository.update_customer(customer_id,customer_data)

        logger.info("Updating customer successfully with customer_id=%s", customer_id)

        return existing_customer
    

    