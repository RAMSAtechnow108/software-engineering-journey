from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.inventory_schema import InventoryResponse,InventoryUpdate
from app.services.inventory_service import InventoryService
from app.repositories.inventory_repository import InventoryRepository




inventory_router = APIRouter()


def get_inventory_service(db:Session =Depends(get_db)):
    
    repository = InventoryRepository(db)

    service = InventoryService(repository)

    return service


@inventory_router.get("/{product_id}",response_model = InventoryResponse)
def get_inventory_by_product_id(
    product_id:int, 
    service: InventoryService = Depends(get_inventory_service)
    ):
    
    return service.get_inventory_by_product_id(product_id)

@inventory_router.patch("/{product_id}",response_model=InventoryResponse)
def update_inventory(product_id:int,inventory_data: InventoryUpdate,service:InventoryService=Depends(get_inventory_service)):
    
    return service.update_inventory(product_id, inventory_data)