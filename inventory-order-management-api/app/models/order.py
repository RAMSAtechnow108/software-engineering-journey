from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import ForeignKey, Numeric,String, DateTime,func,text
from decimal import Decimal
from datetime import datetime

from app.constants.order_constants import OrderStatus


class Order(Base):

    __tablename__ = "Orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey(
            "Customers.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    status: Mapped[OrderStatus] = mapped_column(
        nullable=False
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text(
            "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        )
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="orders"
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order"
    )