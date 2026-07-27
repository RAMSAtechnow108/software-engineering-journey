from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

from app.models.category import Category
from app.schemas.category_schema import CategoryCreate, CategoryUpdate
from app.exceptions.category_exceptions import (
    CategoryNotFoundError,
    DuplicateCategoryError,
    CategoryInUseError
)

logger = logging.getLogger(__name__)


class CategoryRepository:

    def __init__(self, db: Session):
        self.db = db




    def get_all_categories(self):
        try:
            logger.info("Fetching all categories from database.")

            stmt = select(Category)
            result = self.db.execute(stmt)
            categories = result.scalars().all()

            logger.info(
                "Successfully fetched %d categories.",
                len(categories),
            )

            return categories

        except SQLAlchemyError:
            logger.exception("Database error while fetching categories.")
            raise

        except Exception:
            logger.exception("Unexpected error while fetching categories.")
            raise






    def get_category_by_id(self, category_id: int):
        try:
            logger.info(
                "Fetching category with ID %d",
                category_id,
            )

            stmt = select(Category).where(Category.id == category_id)
            result = self.db.execute(stmt)

            category = result.scalar_one_or_none()

            if category is None:
                logger.warning(
                    "Category with ID %d not found.",
                    category_id,
                )
                raise CategoryNotFoundError(category_id)

            logger.info(
                "Category with ID %d fetched successfully.",
                category_id,
            )

            return category

        except CategoryNotFoundError:
            raise

        except SQLAlchemyError:
            logger.exception("Database error while fetching category.")
            raise

        except Exception:
            logger.exception("Unexpected error while fetching category.")
            raise







    def create_category(self, category_data: CategoryCreate):
        try:
            logger.info(
                "Creating category with name: %s",
                category_data.name,
            )

            new_category = Category(name=category_data.name)

            self.db.add(new_category)

            logger.debug(
                "Category object added to SQLAlchemy session."
            )

            self.db.commit()

            logger.debug(
                "Transaction committed successfully."
            )

            self.db.refresh(new_category)

            logger.info(
                "Category created successfully with ID %d",
                new_category.id,
            )

            return new_category

        except IntegrityError:
            self.db.rollback()

            logger.warning(
                "Category '%s' already exists.",
                category_data.name,
            )

            raise DuplicateCategoryError(category_data.name)

        except SQLAlchemyError:
            self.db.rollback()

            logger.exception(
                "Database error while creating category."
            )

            raise

        except Exception:
            self.db.rollback()

            logger.exception(
                "Unexpected error while creating category."
            )

            raise






    def update_category(
        self,
        category_id: int,
        category_data: CategoryUpdate,
    ):
        try:
            logger.info(
                "Updating category with ID %d",
                category_id,
            )

            category = self.get_category_by_id(category_id)

            category.name = category_data.name

            self.db.commit()

            logger.info(
                "Category with ID %d updated successfully.",
                category_id,
            )

            return category

        except CategoryNotFoundError:
            raise

        except DuplicateCategoryError:
            raise

        except IntegrityError:
            self.db.rollback()

            logger.warning(
                "Category '%s' already exists.",
                category_data.name,
            )

            raise DuplicateCategoryError(category_data.name)

        except SQLAlchemyError:
            self.db.rollback()

            logger.exception(
                "Database error while updating category."
            )

            raise

        except Exception:
            self.db.rollback()

            logger.exception(
                "Unexpected error while updating category."
            )

            raise
        
    
    
    def delete_category(self, category_id:int):
        
        try:
            
            logger.info("Deleting category with id=%d",category_id)
            
            category = self.get_category_by_id(category_id)
            
            self.db.delete(category)
            
            self.db.commit()
            logger.info(f"Deleted category with id  {category_id} successfully.")
            
            return category
        except CategoryNotFoundError:
            raise
        
        except IntegrityError:
            self.db.rollback()
            logger.warning(
                "Category with id=%d cannot be deleted because products are assigned to it.",
                category_id
            )
            raise CategoryInUseError(category_id)

        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Database error while deleting category with ID %d", category_id)
            raise
        
        except Exception:
            self.db.rollback()
            logger.exception(f"Unexpected error while deleting category with id {category_id}")
            raise