from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from app.schemas.inventory_schema import InventoryCreate, InventoryResponse



class ProductCreate(BaseModel):
    
    name : str = Field(min_length=3,max_length=100, examples=["abc"])
    price: Decimal = Field(gt=0)
    category_id : int
    
    inventory : InventoryCreate
    


class ProductResponse(BaseModel):
    id : int
    name : str 
    price : Decimal
    category_id : int
    
    inventory : InventoryResponse
    
    model_config = ConfigDict(from_attributes=True)



class ProductUpdate(BaseModel):
    name : str | None = Field(default=None,min_length=3,max_length=100, examples=["abc"])
    price : Decimal | None = Field(default=None,gt=0)
    