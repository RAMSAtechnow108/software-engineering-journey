from fastapi import APIRouter
from fastapi import Depends
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService



router = APIRouter()



def get_product_service():
    
    repository = ProductRepository()

    service = ProductService(repository)

    return service



@router.get("/")
def get_products(service:ProductService = Depends(get_product_service)):
    return service.get_products()