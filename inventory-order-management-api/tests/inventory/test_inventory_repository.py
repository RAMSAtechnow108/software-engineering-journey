
import pytest
from unittest.mock import MagicMock

from sqlalchemy.exc import SQLAlchemyError

from app.models.inventory import Inventory
from app.schemas.inventory_schema import InventoryUpdate
from app.repositories.inventory_repository import InventoryRepository
from app.exceptions.inventory_exceptions import (
    InventoryNotFoundError,
    InsufficientInventoryError,
)


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def repository(db):
    return InventoryRepository(db)


@pytest.fixture
def inventory():
    return Inventory(
        product_id=101,
        total_quantity=10,
        reserved_quantity=4,
    )


def test_update_inventory_success(
    repository,
    db,
    inventory,
    monkeypatch,
):
    monkeypatch.setattr(
        repository,
        "get_inventory_for_update",
        lambda product_id: inventory,
    )

    result = repository.update_inventory(
        product_id=101,
        inventory_data=InventoryUpdate(total_quantity=15),
    )

    assert result.total_quantity == 15
    assert result.reserved_quantity == 4
    assert result.available_quantity == 11

    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(inventory)


def test_update_inventory_rejects_total_below_reserved(
    repository,
    db,
    inventory,
    monkeypatch,
):
    monkeypatch.setattr(
        repository,
        "get_inventory_for_update",
        lambda product_id: inventory,
    )

    with pytest.raises(ValueError, match="reserved quantity"):
        repository.update_inventory(
            product_id=101,
            inventory_data=InventoryUpdate(total_quantity=3),
        )

    # Existing quantity must remain unchanged.
    assert inventory.total_quantity == 10
    assert inventory.reserved_quantity == 4

    db.rollback.assert_called_once_with()
    db.commit.assert_not_called()


def test_update_inventory_rejects_missing_inventory(
    repository,
    db,
    monkeypatch,
):
    monkeypatch.setattr(
        repository,
        "get_inventory_for_update",
        MagicMock(
            side_effect=InventoryNotFoundError(999)
        ),
    )

    with pytest.raises(InventoryNotFoundError):
        repository.update_inventory(
            product_id=999,
            inventory_data=InventoryUpdate(total_quantity=20),
        )

    db.rollback.assert_called_once_with()
    db.commit.assert_not_called()


def test_reserve_stock_success(
    repository,
    db,
    inventory,
    monkeypatch,
):
    monkeypatch.setattr(
        repository,
        "get_inventory_for_update",
        lambda product_id: inventory,
    )

    result = repository.reserve_stock(
        product_id=101,
        quantity=3,
    )

    assert result.reserved_quantity == 7
    assert result.available_quantity == 3
    assert result.total_quantity == 10

    # The service owns the transaction commit.
    db.commit.assert_not_called()


def test_reserve_stock_rejects_insufficient_inventory(
    repository,
    db,
    inventory,
    monkeypatch,
):
    monkeypatch.setattr(
        repository,
        "get_inventory_for_update",
        lambda product_id: inventory,
    )

    with pytest.raises(InsufficientInventoryError):
        repository.reserve_stock(
            product_id=101,
            quantity=7,
        )

    assert inventory.reserved_quantity == 4
    assert inventory.total_quantity == 10

    # No stock should be changed on rejection.
    db.commit.assert_not_called()


def test_update_inventory_rolls_back_on_database_error(
    repository,
    db,
    inventory,
    monkeypatch,
):
    monkeypatch.setattr(
        repository,
        "get_inventory_for_update",
        lambda product_id: inventory,
    )

    db.commit.side_effect = SQLAlchemyError(
        "Simulated database failure"
    )

    with pytest.raises(SQLAlchemyError):
        repository.update_inventory(
            product_id=101,
            inventory_data=InventoryUpdate(total_quantity=15),
        )

    db.rollback.assert_called_once_with()

