from fastapi import FastAPI
from  app.routers.product_router import router
from app.exceptions.product_exceptions import ProductNotFoundError
from app.handlers.exception_handlers import product_not_found_handler

from app.core.database import Base,engine
from app.models.product import Product


app = FastAPI()


Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "API is running"}

app.include_router(router, prefix="/products")
app.add_exception_handler(ProductNotFoundError,product_not_found_handler)
