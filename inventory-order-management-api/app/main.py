from fastapi import FastAPI

from app.routers.product_router import product_router
from app.routers.category_router import category_router
from app.routers.inventory_router import inventory_router
from app.routers.customer_router import customer_router

from app.exceptions.app_exception import AppException
from app.handlers.exception_handlers import app_exception_handler
from app.handlers.global_handler import global_exception_handler

from app.core.database import Base,engine


from app.core.logging_config import setup_logging


setup_logging()

app = FastAPI()


Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "API is running"}

app.include_router(product_router, prefix="/products",tags=["Products"])

app.include_router(category_router,prefix="/categories",tags=["Categories"])

app.include_router(inventory_router,prefix="/inventory",tags=["Inventory"])

app.include_router(customer_router, prefix="/customer",tags=["Customer"])

app.add_exception_handler(AppException,app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)