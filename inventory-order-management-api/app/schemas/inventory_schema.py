from pydantic import BaseModel, Field, ConfigDict

    
class InventoryCreate(BaseModel):
    total_quantity : int = Field(default=0)


class InventoryResponse(BaseModel):
    total_quantity : int = Field(ge=0)
    reserved_quantity : int = Field(ge=0)
    available_quantity : int = Field(ge=0)
    
    model_config = ConfigDict(from_attributes=True)
    
class InventoryUpdate(BaseModel):
    total_quantity: int = Field(ge=0)
    
