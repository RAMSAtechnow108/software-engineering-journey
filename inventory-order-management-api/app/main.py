from fastapi import FastAPI
from  app.routers.product_router import router



app = FastAPI()



@app.get("/")
def home():
    return {"message": "API is running"}

app.include_router(router, prefix="/products")

