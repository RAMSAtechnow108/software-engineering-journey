from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.core.database import Base



class Product(Base):
    __tablename__ = "Products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[Decimal] = mapped_column(Numeric(10,2))
    quantity: Mapped[int] = mapped_column()
    
    category_id: Mapped[int] = mapped_column(ForeignKey("Categories.id",ondelete="RESTRICT"))
    
    category: Mapped["Category"] = relationship(back_populates="products")

    
    