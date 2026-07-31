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
from fastapi import Query




category_router = APIRouter()


def get_category_service(db: Session = Depends(get_db)):
    repository = CategoryRepository(db)
    service = CategoryService(repository)
    return service




@category_router.get("/",response_model=list[CategoryResponse])
def get_all_categories(
    page: int = Query(default=1,ge=1),
    limit: int = Query(default=2, ge=1, le=100),
    sort_by: str = Query(default="name"),
    order: str = Query(default="asc"),
    category_name : str | None = Query(default=None),
    service: CategoryService = Depends(get_category_service)
    ):
    
    return service.get_all_categories(page,limit,sort_by,order,category_name)


@category_router.get("/{category_id}",response_model = CategoryResponse)
def get_category_by_id(category_id:int, service:CategoryService = Depends(get_category_service)):
    
    return service.get_category_by_id(category_id)


@category_router.post("/",status_code=201,response_model = CategoryResponse)
def create_category(category:CategoryCreate,service:CategoryService = Depends(get_category_service)):
    
    return service.create_category(category)


@category_router.patch("/{category_id}",response_model = CategoryResponse)
def update_category(category_id:int, category:CategoryUpdate, service:CategoryService = Depends(get_category_service)):
    
    return service.update_category(category_id, category)


@category_router.delete("/{category_id}")
def delete_category(category_id:int,service: CategoryService=Depends(get_category_service)):
    
    service.delete_category(category_id)
    return {
        "success": True,
        "message": "Category deleted successfully"
    }
