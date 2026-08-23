from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, String, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OrderItem(Base):

    __tablename__ = "OrderItems"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey(
            "Orders.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            "Products.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    product_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        nullable=False
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    order: Mapped["Order"] = relationship(
        back_populates="items"
    )