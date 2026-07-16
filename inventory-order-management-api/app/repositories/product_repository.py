from app.schemas.product_schema import ProductCreate,ProductUpdate
from app.exceptions.product_exceptions import ProductNotFoundError


class ProductRepository:

    existing_products = [

            {
                "id": 1,
                "name": "Laptop",
                "price": 55000,
                "quantity": 10
            },
            {
                "id": 2,
                "name": "Mouse",
                "price": 800,
                "quantity": 50
            },
            {
                "id": 3,
                "name": "Keyboard",
                "price": 1500,
                "quantity": 35
            },
            {
                "id": 4,
                "name": "Monitor",
                "price": 12000,
                "quantity": 15
            },
            {
                "id": 5,
                "name": "Printer",
                "price": 8500,
                "quantity": 8
            },
            {
                "id": 6,
                "name": "Webcam",
                "price": 2500,
                "quantity": 20
            },
            {
                "id": 7,
                "name": "Headphones",
                "price": 3000,
                "quantity": 25
            },
            {
                "id": 8,
                "name": "Speaker",
                "price": 4500,
                "quantity": 18
            },
            {
                "id": 9,
                "name": "SSD",
                "price": 6000,
                "quantity": 12
            },
            {
                "id": 10,
                "name": "Power Bank",
                "price": 1800,
                "quantity": 40
            }
        ]
  
    def get_products(self):
        return self.existing_products


    def get_product(self,id:int):
       
        for product in self.existing_products:
            if product["id"]==id:
                return product
        raise ProductNotFoundError(f"Product with id {id} not found")
     
        
    def create_product(self,product: ProductCreate):
        last_id = self.existing_products[-1]["id"]+1
        new_product = {
            "id":last_id,
            "name": product.name,
            "price": product.price,
            "quantity":product.quantity
        }
        self.existing_products.append(new_product)

        return new_product

    
    def update_product(self, id:int,product:ProductUpdate):
        existing_product = self.get_product(id)
        
        if product.name is not None:
            existing_product["name"] = product.name
        if product.price is not None:
            existing_product["price"] = product.price
        if product.quantity is not None:
            existing_product["quantity"] = product.quantity
        return existing_product
    
    
    def delete_product(self,id:int):
        existing_product = self.get_product(id)
        self.existing_products.remove(existing_product)
        