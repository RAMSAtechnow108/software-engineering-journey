from fastapi import APIRouter
from fastapi import Depends
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService
from app.schemas.product_schema import ProductCreate, ProductResponse,ProductUpdate
from sqlalchemy.orm import Session
from app.core.database import get_db


router = APIRouter()



def get_product_service(db:Session= Depends(get_db)):
    
    repository = ProductRepository(db)

    service = ProductService(repository)

    return service



@router.get("/",response_model = list[ProductResponse])
def get_products(service:ProductService = Depends(get_product_service)):
    return service.get_products()


@router.get("/{id}",response_model = ProductResponse)
def get_product(id:int ,service:ProductService = Depends(get_product_service)):
    return service.get_product(id)



@router.post("/",status_code=201, response_model=ProductResponse)
def create_product(product: ProductCreate, service:ProductService = Depends(get_product_service)):
    return service.create_product(product)


@router.patch("/{id}",response_model = ProductResponse)
def update_product(id: int, product: ProductUpdate,service:ProductService = Depends(get_product_service)):
    return service.update_product(id,product)
    

@router.delete("/{id}")
def delete_product(id: int, service:ProductService = Depends(get_product_service)):
    service.delete_product(id)
    return { 
            "success": True,
            "message": "Product deleted successfully"
        }
    
    
    
