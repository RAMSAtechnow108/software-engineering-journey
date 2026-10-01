from pydantic import BaseModel , Field, EmailStr,ConfigDict

from datetime import datetime

from app.constants.user_constants import UserRole
from app.schemas.customer_schema import CustomerResponse


class UserCreate(BaseModel):
    
    name: str = Field(min_length=3, max_length=100)
    
    email : EmailStr
    
    phone: str = Field(min_length=10, max_length=20)

    password: str = Field(min_length=8,max_length=120)



class UserResponse(BaseModel):
    
    id:int
    email: EmailStr
    role: UserRole
    is_active: bool
    customer_id: int | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)



class UserRegistrationResponse(BaseModel):
    
    user: UserResponse
    customer: CustomerResponse