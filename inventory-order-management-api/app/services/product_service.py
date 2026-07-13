
class ProductService:
    
    
    def __init__(self, repository):
        self.repository = repository


    def get_products(self):
        return self.repository.get_products()