from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime


class OrderItemCreate(BaseModel):
    
    product_id: int
    
    quantity: int = Field(ge=1)
    

class OrderItemResponse(BaseModel):
    
    id: int
    order_id: int
    product_id:int
    product_name:int
    quantity: int
    unitprice:Decimal
    created_at: datetime
    
    model_config = ConfigDict(from_attributes= True)