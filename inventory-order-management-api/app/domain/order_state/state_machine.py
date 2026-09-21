from app.constants.order_constants import OrderStatus
from app.exceptions.order_exceptions import (
    InvalidOrderStatusTransitionError
)


class OrderStateMachine:

    ALLOWED_TRANSITIONS = {

        OrderStatus.PENDING: {
            OrderStatus.CONFIRMED,
            OrderStatus.CANCELLED,
            OrderStatus.EXPIRED,
        },

        OrderStatus.CONFIRMED: {
            OrderStatus.SHIPPED,
        },

        OrderStatus.SHIPPED: {
            OrderStatus.DELIVERED,
        },

        OrderStatus.CANCELLED: set(),

        OrderStatus.EXPIRED: set(),

        OrderStatus.DELIVERED: set(),
    }

    @classmethod
    def validate_transition(
        cls,
        current_status: OrderStatus,
        new_status: OrderStatus
    ) -> None:

        allowed_statuses = cls.ALLOWED_TRANSITIONS.get(
            current_status,
            set()
        )

        if new_status not in allowed_statuses:
            raise InvalidOrderStatusTransitionError(
                current_status=current_status,
                new_status=new_status
            )