from pydantic import BaseModel, Field, ConfigDict, EmailStr, model_validator
from datetime import datetime




class CustomerCreate(BaseModel):
    
    name: str = Field(min_length=3, max_length=100)

    email: str = Field(max_length=244)

    phone: str = Field(min_length=10, max_length=20)


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    

class CustomerUpdate(BaseModel):
    
    name: str | None = Field(default=None, min_length=3, max_length=100)
    @model_validator(mode="after")
    def validate_update_data(self):
        if not self.model_fields_set:
            raise ValueError("At least one field is required for update")
        
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("Name cannot be null")
        
        return self