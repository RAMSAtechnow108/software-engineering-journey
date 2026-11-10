
import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.exceptions.inventory_exceptions import (
    InsufficientInventoryError,
    InventoryNotFoundError,
)
from app.models.inventory import Inventory
from app.schemas.inventory_schema import InventoryUpdate


logger = logging.getLogger(__name__)


class InventoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_inventory_by_product_id(self, product_id: int):
        try:
            logger.info(
                "Getting inventory for product_id=%s",
                product_id,
            )

            result = self.db.execute(
                select(Inventory).where(
                    Inventory.product_id == product_id
                )
            )

            inventory = result.scalar_one_or_none()

            if inventory is None:
                raise InventoryNotFoundError(product_id)

            return inventory

        except InventoryNotFoundError:
            raise

        except SQLAlchemyError:
            logger.exception(
                "Database error getting inventory for product_id=%s",
                product_id,
            )
            raise

    def get_inventory_for_update(self, product_id: int):
        try:
            logger.info(
                "Locking inventory for product_id=%s",
                product_id,
            )

            result = self.db.execute(
                select(Inventory)
                .where(Inventory.product_id == product_id)
                .with_for_update()
            )

            inventory = result.scalar_one_or_none()

            if inventory is None:
                raise InventoryNotFoundError(product_id)

            return inventory

        except InventoryNotFoundError:
            raise

        except SQLAlchemyError:
            logger.exception(
                "Database error locking inventory for product_id=%s",
                product_id,
            )
            raise

    def update_inventory(
        self,
        product_id: int,
        inventory_data: InventoryUpdate,
    ):
        try:
            inventory = self.get_inventory_for_update(product_id)
            new_total = inventory_data.total_quantity

            if new_total < inventory.reserved_quantity:
                raise ValueError(
                    f"Total quantity ({new_total}) cannot be less "
                    f"than reserved quantity "
                    f"({inventory.reserved_quantity}) "
                    f"for product_id={product_id}"
                )

            inventory.total_quantity = new_total

            self.db.commit()
            self.db.refresh(inventory)

            logger.info(
                "Inventory updated for product_id=%s",
                product_id,
            )

            return inventory

        except Exception:
            self.db.rollback()
            logger.exception(
                "Failed to update inventory for product_id=%s",
                product_id,
            )
            raise

    def reserve_stock(self, product_id: int, quantity: int):
        try:
            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero")

            inventory = self.get_inventory_for_update(product_id)
            available_quantity = inventory.available_quantity

            if available_quantity < quantity:
                raise InsufficientInventoryError(
                    product_id=product_id,
                    requested_quantity=quantity,
                    available_quantity=available_quantity,
                )

            inventory.reserved_quantity += quantity

            logger.info(
                "Stock reserved: product_id=%s, quantity=%s, "
                "reserved_quantity=%s",
                product_id,
                quantity,
                inventory.reserved_quantity,
            )

            # No commit here. The calling service owns the transaction.
            return inventory

        except (InsufficientInventoryError, ValueError):
            raise

        except SQLAlchemyError:
            logger.exception(
                "Database error reserving stock for product_id=%s",
                product_id,
            )
            raise

    def deduct_reserved_stock(self, product_id: int, quantity: int):
        """Deduct shipped stock without committing the transaction."""
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        inventory = self.get_inventory_for_update(product_id)

        if (
            inventory.total_quantity < quantity
            or inventory.reserved_quantity < quantity
        ):
            raise RuntimeError(
                "Inventory reservation mismatch for "
                f"product_id={product_id}: "
                f"total={inventory.total_quantity}, "
                f"reserved={inventory.reserved_quantity}, "
                f"requested={quantity}"
            )

        inventory.total_quantity -= quantity
        inventory.reserved_quantity -= quantity

        logger.info(
            "Shipped stock deducted: product_id=%s, quantity=%s, "
            "total_quantity=%s, reserved_quantity=%s",
            product_id,
            quantity,
            inventory.total_quantity,
            inventory.reserved_quantity,
        )

        # Intentionally no commit or rollback.
        return inventory
