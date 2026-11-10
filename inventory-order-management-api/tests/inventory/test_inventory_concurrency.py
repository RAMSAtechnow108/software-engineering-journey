
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

from app.models.category import Category
from app.models.product import Product
from app.models.inventory import Inventory
from app.repositories.inventory_repository import InventoryRepository
from app.exceptions.inventory_exceptions import InsufficientInventoryError
from tests.database import TestSessionLocal


def test_concurrent_reservations_do_not_oversell():
    """
    Two independent DB sessions try to reserve 7 units each
    when only 10 units are available.

    Expected: one succeeds, one fails, and only 7 units
    are reserved.
    """
    setup_db = TestSessionLocal()
    category = None
    product = None
    inventory = None

    try:
        unique_id = uuid4().hex

        # Create isolated test data.
        category = Category(name=f"Concurrency-{unique_id}")
        setup_db.add(category)
        setup_db.flush()

        product = Product(
            name=f"Concurrency-{unique_id}",
            price=10,
            category_id=category.id,
        )
        setup_db.add(product)
        setup_db.flush()

        inventory = Inventory(
            product_id=product.id,
            total_quantity=10,
            reserved_quantity=0,
        )
        setup_db.add(inventory)
        setup_db.commit()

        product_id = product.id

        # Both workers start their reservation attempt together.
        barrier = Barrier(2)

        def reserve_seven_units():
            db = TestSessionLocal()

            try:
                repository = InventoryRepository(db)
                barrier.wait(timeout=10)

                repository.reserve_stock(product_id, 7)
                db.commit()
                return "success"

            except InsufficientInventoryError:
                db.rollback()
                return "insufficient_stock"

            except Exception:
                db.rollback()
                raise

            finally:
                db.close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(reserve_seven_units),
                executor.submit(reserve_seven_units),
            ]
            results = [future.result(timeout=30) for future in futures]

        # Exactly one request must succeed.
        assert results.count("success") == 1
        assert results.count("insufficient_stock") == 1

        # Verify the final state using a fresh database session.
        verify_db = TestSessionLocal()
        try:
            final_inventory = (
                verify_db.query(Inventory)
                .filter(Inventory.product_id == product_id)
                .one()
            )

            assert final_inventory.reserved_quantity == 7
            assert final_inventory.available_quantity == 3
        finally:
            verify_db.close()

    finally:
        # Delete only the records created by this test.
        try:
            setup_db.rollback()

            if inventory is not None and inventory.id is not None:
                setup_db.delete(inventory)
            if product is not None and product.id is not None:
                setup_db.delete(product)
            if category is not None and category.id is not None:
                setup_db.delete(category)

            setup_db.commit()
        finally:
            setup_db.close()