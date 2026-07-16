from app.schemas.product_schema import ProductCreate,ProductUpdate



class ProductService:
    
    
    def __init__(self, repository):
        self.repository = repository

    def get_products(self):
        return self.repository.get_products()

    def get_product(self,id:int):
        return self.repository.get_product(id)
    
    
    def create_product(self,product: ProductCreate):
        return self.repository.create_product(product)
    
    def update_product(self,id: int, product:ProductUpdate):
        return self.repository.update_product(id,product)
    
    
    def delete_product(self,id:int):
        return self.repository.delete_product(id)
        