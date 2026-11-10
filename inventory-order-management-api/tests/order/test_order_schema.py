
import pytest
from pydantic import ValidationError

from app.schemas.order_schema import OrderCreate


def test_order_accepts_valid_items():
    order = OrderCreate(
        items=[
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 3},
        ]
    )

    assert len(order.items) == 2


def test_order_rejects_empty_items():
    with pytest.raises(ValidationError):
        OrderCreate(items=[])


@pytest.mark.parametrize("quantity", [0, -1])
def test_order_rejects_non_positive_quantity(quantity):
    with pytest.raises(ValidationError):
        OrderCreate(
            items=[{"product_id": 1, "quantity": quantity}]
        )


def test_order_rejects_duplicate_product_ids():
    with pytest.raises(
        ValidationError,
        match="Duplicate product IDs",
    ):
        OrderCreate(
            items=[
                {"product_id": 1, "quantity": 2},
                {"product_id": 1, "quantity": 3},
            ]
        )
