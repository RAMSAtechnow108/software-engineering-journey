from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.constants.user_constants import UserRole




class User(Base):
    
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    password_hash: Mapped[str] = mapped_column(String(255),nullable=False)

    role: Mapped[UserRole] = mapped_column(default=UserRole.CUSTOMER, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True,nullable=False)

    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, unique=True)

    created_at: Mapped[datetime] = mapped_column(DateTime,nullable=False, server_default=func.now())

    customer = relationship("Customer", back_populates="user")