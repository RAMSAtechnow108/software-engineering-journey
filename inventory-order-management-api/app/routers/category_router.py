from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.repositories.category_repository import CategoryRepository
from app.services.category_service import CategoryService

from app.schemas.category_schema import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate
)



category_router = APIRouter()


def get_category_service(db: Session = Depends(get_db)):
    repository = CategoryRepository(db)
    service = CategoryService(repository)
    return service




@category_router.get("/",response_model=list[CategoryResponse])
def get_all_categories(service: CategoryService = Depends(get_category_service)):
    
    return service.get_all_categories()


@category_router.get("/{category_id}",response_model = CategoryResponse)
def get_category_by_id(id:int, service:CategoryService = Depends(get_category_service)):
    
    return service.get_category_by_id(id)


@category_router.post("/",status_code=201,response_model = CategoryResponse)
def create_category(category:CategoryCreate,service:CategoryService = Depends(get_category_service)):
    
    return service.create_category(category)


@category_router.patch("/{category_id}",response_model = CategoryResponse)
def update_category(id:int, category:CategoryUpdate, service:CategoryService = Depends(get_category_service)):
    
    return service.update_category(id, category)


@category_router.delete("/{category_id}")
def delete_category(id:int,service: CategoryService=Depends(get_category_service)):
    
    service.delete_category(id)
    return {
        "success": True,
        "message": "Category deleted successfully"
    }
