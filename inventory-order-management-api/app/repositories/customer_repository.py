import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer_schema import CustomerCreate, CustomerUpdate
from app.exceptions.customer_exceptions import (
    CustomerNotFoundError,
    DuplicateCustomerEmailError,
    DuplicateCustomerPhoneError,
)


logger = logging.getLogger(__name__)


class CustomerRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_customer_by_id(self, customer_id: int) -> Customer:

        try:
            logger.info(
                "Fetching customer with customer_id=%s",
                customer_id,
            )

            result = self.db.execute(
                select(Customer).where(Customer.id == customer_id)
            )

            customer = result.scalar_one_or_none()

            if customer is None:
                logger.warning(
                    "Customer not found with customer_id=%s",
                    customer_id,
                )
                raise CustomerNotFoundError(customer_id)

            logger.info(
                "Customer fetched successfully with customer_id=%s",
                customer_id,
            )

            return customer

        except CustomerNotFoundError:
            raise

        except SQLAlchemyError:
            logger.exception(
                "Database error while fetching customer_id=%s",
                customer_id,
            )
            raise

        except Exception:
            logger.exception(
                "Unexpected error while fetching customer_id=%s",
                customer_id,
            )
            raise

    def create_customer(
        self,
        customer_data: CustomerCreate,
    ) -> Customer:

        logger.info("Creating customer")

        try:
            existing_email = self.db.execute(
                select(Customer).where(
                    Customer.email == customer_data.email
                )
            ).scalar_one_or_none()

            if existing_email:
                raise DuplicateCustomerEmailError(
                    customer_data.email
                )

            existing_phone = self.db.execute(
                select(Customer).where(
                    Customer.phone == customer_data.phone
                )
            ).scalar_one_or_none()

            if existing_phone:
                raise DuplicateCustomerPhoneError(
                    customer_data.phone
                )

            new_customer = Customer(
                name=customer_data.name,
                email=customer_data.email,
                phone=customer_data.phone,
            )

            self.db.add(new_customer)
            self.db.commit()
            self.db.refresh(new_customer)

            logger.info(
                "Customer created successfully with customer_id=%s",
                new_customer.id,
            )

            return new_customer

        except (
            DuplicateCustomerEmailError,
            DuplicateCustomerPhoneError,
        ):
            self.db.rollback()
            raise

        except IntegrityError as exc:
            self.db.rollback()

            constraint_name = str(exc.orig)

            if "uq_customers_email" in constraint_name:
                logger.warning(
                    "Customer creation rejected due to duplicate email"
                )
                raise DuplicateCustomerEmailError(
                    customer_data.email
                ) from exc

            if "uq_customers_phone" in constraint_name:
                logger.warning(
                    "Customer creation rejected due to duplicate phone"
                )
                raise DuplicateCustomerPhoneError(
                    customer_data.phone
                ) from exc

            logger.exception(
                "Unexpected integrity error while creating customer"
            )
            raise

        except SQLAlchemyError:
            self.db.rollback()
            logger.exception(
                "Database error while creating customer"
            )
            raise

        except Exception:
            self.db.rollback()
            logger.exception(
                "Unexpected error while creating customer"
            )
            raise

    def add_customer(
        self,
        customer_data: CustomerCreate,
    ) -> Customer:
        """
        Adds a customer to the current transaction.

        This method intentionally does not commit.
        The calling service controls the transaction.
        """

        logger.info("Adding customer to current transaction")

        existing_email = self.db.execute(
            select(Customer).where(
                Customer.email == customer_data.email
            )
        ).scalar_one_or_none()

        if existing_email:
            raise DuplicateCustomerEmailError(
                customer_data.email
            )

        existing_phone = self.db.execute(
            select(Customer).where(
                Customer.phone == customer_data.phone
            )
        ).scalar_one_or_none()

        if existing_phone:
            raise DuplicateCustomerPhoneError(
                customer_data.phone
            )

        new_customer = Customer(
            name=customer_data.name,
            email=customer_data.email,
            phone=customer_data.phone,
        )

        self.db.add(new_customer)
        self.db.flush()

        logger.info(
            "Customer added to transaction with customer_id=%s",
            new_customer.id,
        )

        return new_customer

    def update_customer(
        self,
        customer_id: int,
        customer_data: CustomerUpdate,
    ) -> Customer:

        logger.info(
            "Updating customer with customer_id=%s",
            customer_id,
        )

        # If the customer does not exist, the custom exception
        # propagates before any update transaction begins.
        existing_customer = self.get_customer_by_id(customer_id)

        update_data = customer_data.model_dump(
            exclude_unset=True
        )

        try:
            for field, value in update_data.items():
                setattr(existing_customer, field, value)

            self.db.commit()
            self.db.refresh(existing_customer)

            logger.info(
                "Customer updated successfully with customer_id=%s",
                customer_id,
            )

            return existing_customer

        except SQLAlchemyError:
            self.db.rollback()
            logger.exception(
                "Database error while updating customer_id=%s",
                customer_id,
            )
            raise

        except Exception:
            self.db.rollback()
            logger.exception(
                "Unexpected error while updating customer_id=%s",
                customer_id,
            )
            raise