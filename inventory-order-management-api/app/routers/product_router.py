from fastapi import APIRouter
from fastapi import Depends
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService
from app.schemas.product_schema import ProductCreate, ProductResponse,ProductUpdate
from sqlalchemy.orm import Session
from app.core.database import get_db
from fastapi import Query



product_router = APIRouter()



def get_product_service(db:Session= Depends(get_db)):
    
    repository = ProductRepository(db)

    service = ProductService(repository)

    return service



@product_router.get("/",response_model = list[ProductResponse])
def get_products(
    page: int = Query(default=1, ge=1), 
    limit: int = Query(default=10, ge=1,le=100),
    sort_by :str = Query(default="name"),
    order: str = Query(default="asc"),
    category_id: int | None = Query(default=None, ge=1),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    search: str | None = Query(default=None),
    service:ProductService = Depends(get_product_service)
    ):
        
    return service.get_products(page,limit,sort_by,order,category_id,min_price,max_price,search)


@product_router.get("/{product_id}",response_model = ProductResponse)
def get_product(product_id:int ,service:ProductService = Depends(get_product_service)):
    return service.get_product_by_id(product_id)



@product_router.post("/",status_code=201, response_model=ProductResponse)
def create_product(product: ProductCreate, service:ProductService = Depends(get_product_service)):
    return service.create_product(product)


@product_router.patch("/{product_id}",response_model = ProductResponse)
def update_product(product_id: int, product: ProductUpdate,service:ProductService = Depends(get_product_service)):
    
    
    return service.update_product(product_id,product)
    

@product_router.delete("/{product_id}")
def delete_product(product_id: int, service:ProductService = Depends(get_product_service)):
    service.delete_product(product_id)
    return { 
            "success": True,
            "message": "Product deleted successfully"
        }
    
    
    
