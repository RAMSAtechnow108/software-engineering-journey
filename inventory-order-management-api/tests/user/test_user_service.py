from unittest.mock import Mock

import pytest
from sqlalchemy import select

from app.services.user_service import UserService
from app.schemas.user_schema import UserCreate
from app.models.customer import Customer
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.customer_repository import CustomerRepository


def test_registration_rolls_back_when_user_creation_fails(db):
    user_repository = UserRepository(db)
    customer_repository = CustomerRepository(db)

    service = UserService(
        user_repository=user_repository,
        customer_repository=customer_repository
    )

    # User creation ko intentionally fail karwa rahe hain
    user_repository.create_user = Mock(
        side_effect=Exception("Simulated user creation failure")
    )

    user_data = UserCreate(
        name="Rollback User",
        email="rollback@example.com",
        phone="9000000030",
        password="StrongPass123"
    )

    with pytest.raises(Exception, match="Simulated user creation failure"):
        service.register_customer(user_data)

    # Rollback ke baad Customer DB mein nahi hona chahiye
    customer = db.execute(
        select(Customer).where(
            Customer.email == "rollback@example.com"
        )
    ).scalar_one_or_none()

    assert customer is None

    # User bhi DB mein nahi hona chahiye
    user = db.execute(
        select(User).where(
            User.email == "rollback@example.com"
        )
    ).scalar_one_or_none()

    assert user is None
    
    
