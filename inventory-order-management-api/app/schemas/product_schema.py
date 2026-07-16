from pydantic import BaseModel
from decimal import Decimal



class ProductCreate(BaseModel):
    
    name : str
    price: Decimal
    quantity : int
    
    


class ProductResponse(ProductCreate):
    id : int
    
    

class ProductUpdate(BaseModel):
    name : str | None = None
    price : Decimal | None = None
    quantity : int | None = None