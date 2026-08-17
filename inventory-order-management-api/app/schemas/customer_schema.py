from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime




class CustomerCreate(BaseModel):
    
    name: str = Field(min_length=3, max_length=100)

    email: str = Field(max_length=244)

    phone: str = Field(min_length=10, max_length=20)


class CustomerResponse(CustomerCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    

class CustomerUpdate(BaseModel):
    
    name: str | None = Field(default=None, min_length=3, max_length=100)