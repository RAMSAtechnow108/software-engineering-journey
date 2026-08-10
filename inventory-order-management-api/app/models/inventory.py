from sqlalchemy import ForeignKey,DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from datetime import datetime
from sqlalchemy import func


class Inventory(Base):
    
    __tablename__ = "Inventory"

    id : Mapped[int] = mapped_column(primary_key=True)
    
    product_id : Mapped[int] = mapped_column(ForeignKey("Products.id", ondelete="CASCADE"), unique=True)

    total_quantity : Mapped[int] = mapped_column(default=0)

    reserved_quantity : Mapped[int] = mapped_column(default=0)

    created_at : Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    updated_at : Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    product : Mapped["Product"] = relationship(back_populates="inventory")
    
    
    @property
    def available_quantity(self) ->int:
        return self.total_quantity - self.reserved_quantity