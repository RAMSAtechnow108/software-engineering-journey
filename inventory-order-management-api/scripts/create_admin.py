import logging

from app.core.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.security.password import hash_password


logger = logging.getLogger(__name__)

def create_admin():
    email="admin@example.com"
    password="AdminPass123"

    db = SessionLocal()


    try:
        
        user_repository = UserRepository(db)
        existing_user = user_repository.get_user_by_email(email)
        if existing_user:
            logger.info("User with email=%s already exists",email)
            return 
        
        password_hash = hash_password(password)

        user = user_repository.create_admin_user(email=email, password_hash=password_hash)

        db.commit()

        logger.info("Admin created successfully with user_id=%s", user.id)

    except Exception:
        db.rollback()
        logger.exception("Failed to create admin")
        raise

    finally: db.close()


if __name__ == "__main__":
    create_admin()