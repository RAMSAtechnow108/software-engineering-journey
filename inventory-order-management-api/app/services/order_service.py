
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.constants.order_constants import OrderStatus
from app.constants.user_constants import UserRole
from app.domain.order_state.state_machine import OrderStateMachine
from app.exceptions.order_exceptions import OrderNotFoundError
from app.models.user import User
from app.schemas.order_schema import OrderCreate


logger = logging.getLogger(__name__)


class OrderService:
    def __init__(
        self,
        order_repository,
        customer_repository,
        product_repository,
        inventory_repository,
        order_item_repository,
        order_state_machine=OrderStateMachine,
    ):
        self.order_repository = order_repository
        self.customer_repository = customer_repository
        self.product_repository = product_repository
        self.inventory_repository = inventory_repository
        self.order_item_repository = order_item_repository
        self.order_state_machine = order_state_machine

    def get_order_by_id(self, order_id: int, current_user: User):
        logger.info("Getting order with order_id=%s", order_id)

        order = self.order_repository.get_order_by_id(order_id)

        if order is None:
            raise OrderNotFoundError(order_id)

        if current_user.role != UserRole.ADMIN:
            if current_user.customer_id != order.customer_id:
                raise HTTPException(
                    status_code=403,
                    detail="You do not have access to this order",
                )

        logger.info(
            "Order fetched successfully with order_id=%s",
            order_id,
        )
        return order

    def create_order(
        self,
        customer_id: int,
        order_data: OrderCreate,
        current_user: User,
    ):
        logger.info("Creating order for customer_id=%s", customer_id)

        if current_user.role != UserRole.ADMIN:
            if current_user.customer_id != customer_id:
                raise HTTPException(
                    status_code=403,
                    detail="You do not have access to this customer",
                )

        try:
            self.customer_repository.get_customer_by_id(customer_id)

            reservation_until = datetime.now() + timedelta(minutes=15)

            order = self.order_repository.create_order(
                customer_id=customer_id,
                reservation_until=reservation_until,
            )

            total_amount = Decimal("0.00")

            # Consistent product ordering reduces the chance of deadlocks.
            for item in sorted(
                order_data.items,
                key=lambda item: item.product_id,
            ):
                product = self.product_repository.get_product_by_id(
                    item.product_id
                )

                self.inventory_repository.reserve_stock(
                    product_id=item.product_id,
                    quantity=item.quantity,
                )

                self.order_item_repository.create_order_item(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    quantity=item.quantity,
                    unit_price=product.price,
                )

                total_amount += product.price * item.quantity

            order.total_amount = total_amount

            self.order_repository.db.commit()
            self.order_repository.db.refresh(order)

            logger.info(
                "Order created successfully: order_id=%s",
                order.id,
            )
            return order

        except Exception:
            self.order_repository.db.rollback()
            logger.exception(
                "Error while creating order for customer_id=%s",
                customer_id,
            )
            raise


    def expire_orders(self, current_time: datetime):
        logger.info(
            "Starting expired order processing at=%s",
            current_time,
        )

        expired_orders = self.order_repository.get_expired_orders(
            current_time
        )
        expired_order_ids = [order.id for order in expired_orders]

        processed_count = 0
        failed_orders = []

        for order_id in expired_order_ids:
            try:
                order = self.order_repository.get_order_for_update(order_id)

                if order is None:
                    continue

                if order.status != OrderStatus.PENDING:
                    continue

                if order.reservation_until > current_time:
                    continue

                order_items = self.order_item_repository.get_order_items(
                    order.id
                )

                with self.order_repository.db.begin_nested():
                    for item in sorted(
                        order_items,
                        key=lambda item: item.product_id,
                    ):
                        inventory = (
                            self.inventory_repository.get_inventory_for_update(
                                item.product_id
                            )
                        )

                        if inventory is None:
                            raise ValueError(
                                f"Inventory not found for "
                                f"product_id={item.product_id}"
                            )

                        if inventory.reserved_quantity < item.quantity:
                            raise ValueError(
                                "Insufficient reserved quantity "
                                f"for product_id={item.product_id}"
                            )

                        inventory.reserved_quantity -= item.quantity

                    self.order_state_machine.validate_transition(
                        order.status,
                        OrderStatus.EXPIRED,
                    )
                    order.status = OrderStatus.EXPIRED

                self.order_repository.db.commit()
                processed_count += 1

                logger.info(
                    "Expired order processed successfully, order_id=%s",
                    order_id,
                )

            except Exception as exc:
                self.order_repository.db.rollback()
                failed_orders.append((order_id, str(exc)))

                logger.exception(
                    "Failed to expire order_id=%s; continuing with other "
                    "expired orders",
                    order_id,
                )

        logger.info(
            "Expired order processing finished: processed=%s, failed=%s",
            processed_count,
            len(failed_orders),
        )

        return {
            "processed_count": processed_count,
            "failed_orders": failed_orders,
        }
        
    
    def update_order_status(
        self,
        order_id: int,
        new_status: OrderStatus,
        current_user: User,
    ):
        logger.info(
            "Updating order status, order_id=%s, new_status=%s",
            order_id,
            new_status,
        )

        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="Only admin can update order status",
            )

        try:
            order = self.order_repository.get_order_for_update(order_id)

            if order is None:
                raise OrderNotFoundError(order_id)

            self.order_state_machine.validate_transition(
                order.status,
                new_status,
            )

            if (
                order.status == OrderStatus.CONFIRMED
                and new_status == OrderStatus.SHIPPED
            ):
                order_items = (
                    self.order_item_repository.get_order_items(order_id)
                )

                for item in sorted(
                    order_items,
                    key=lambda item: item.product_id,
                ):
                    self.inventory_repository.deduct_reserved_stock(
                        product_id=item.product_id,
                        quantity=item.quantity,
                    )

            updated_order = self.order_repository.update_order_status(
                order=order,
                new_status=new_status,
            )

            # Status and inventory changes commit atomically.
            self.order_repository.db.commit()
            self.order_repository.db.refresh(updated_order)

            logger.info(
                "Order status updated successfully, "
                "order_id=%s, new_status=%s",
                order_id,
                new_status,
            )
            return updated_order

        except SQLAlchemyError:
            self.order_repository.db.rollback()
            logger.exception(
                "Database error updating order_id=%s",
                order_id,
            )
            raise

        except Exception:
            self.order_repository.db.rollback()
            logger.exception(
                "Error updating order_id=%s",
                order_id,
            )
            raise

    def cancel_order(self, order_id: int, current_user: User):
        logger.info("Cancelling order, order_id=%s", order_id)

        try:
            order = self.order_repository.get_order_for_update(order_id)

            if order is None:
                raise OrderNotFoundError(order_id)

            if current_user.role != UserRole.ADMIN:
                if current_user.customer_id != order.customer_id:
                    raise HTTPException(
                        status_code=403,
                        detail="You do not have access to cancel this order",
                    )

            self.order_state_machine.validate_transition(
                order.status,
                OrderStatus.CANCELLED,
            )

            logger.info(
                "Order cancellation validated, order_id=%s",
                order_id,
            )

            order_items = self.order_item_repository.get_order_items(
                order.id
            )

            # Release reservations in deterministic product_id order.
            for item in sorted(
                order_items,
                key=lambda item: item.product_id,
            ):
                inventory = (
                    self.inventory_repository.get_inventory_for_update(
                        item.product_id
                    )
                )

                if inventory.reserved_quantity < item.quantity:
                    raise ValueError(
                        "Insufficient reserved quantity "
                        f"for product_id={item.product_id}"
                    )

                inventory.reserved_quantity -= item.quantity

            order.status = OrderStatus.CANCELLED

            self.order_repository.db.commit()
            self.order_repository.db.refresh(order)

            return order

        except SQLAlchemyError:
            self.order_repository.db.rollback()
            logger.exception(
                "Database error while cancelling order, order_id=%s",
                order_id,
            )
            raise

        except Exception:
            self.order_repository.db.rollback()
            logger.exception(
                "Error while cancelling order, order_id=%s",
                order_id,
            )
            raise
