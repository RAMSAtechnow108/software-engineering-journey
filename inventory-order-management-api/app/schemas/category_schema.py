from pydantic import BaseModel, Field,ConfigDict



class CategoryCreate(BaseModel):
    name : str = Field(max_length=100,min_length=3, examples=["abc"])


class CategoryUpdate(CategoryCreate):
    pass
    
    
class CategoryResponse(CategoryCreate):
    id:int
    model_config = ConfigDict(from_attributes=True)