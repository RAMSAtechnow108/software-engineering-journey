from datetime import datetime

from sqlalchemy import String, DateTime, func,text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base



class Customer(Base):
    
    __tablename__ = "Customers"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str] = mapped_column(String(244), nullable=False)

    phone: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), )


    __table_args__ = (
        UniqueConstraint("email", name = "uq_customers_email"),
        UniqueConstraint("phone", name = "uq_customers_phone"),
    )