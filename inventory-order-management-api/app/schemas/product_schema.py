from pydantic import BaseModel, Field
from decimal import Decimal



class ProductCreate(BaseModel):
    
    name : str = Field(min_length=3,max_length=100, examples=["abc"])
    price: Decimal = Field(gt=0)
    quantity : int = Field(ge=0)
    
    


class ProductResponse(ProductCreate):
    id : int
    
    

class ProductUpdate(BaseModel):
    name : str | None = Field(default=None,min_length=3,max_length=100, examples=["abc"])
    price : Decimal | None = Field(default=None,gt=0)
    quantity : int | None = Field(default=None,ge=0)
    