from fastapi import FastAPI
from  app.routers.product_router import router
from app.exceptions.product_exceptions import AppException
from app.handlers.exception_handlers import app_exception_handler
from app.handlers.global_handler import global_exception_handler

from app.core.database import Base,engine
from app.models.product import Product

from app.core.logging_config import setup_logging


setup_logging()

app = FastAPI()


Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "API is running"}

app.include_router(router, prefix="/products")

app.add_exception_handler(AppException,app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)