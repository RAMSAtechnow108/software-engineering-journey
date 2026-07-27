

class CategoryService:
    
    def __init__(self,repository):
        self.repository = repository
    
    
    def get_all_categories(self):

        return self.repository.get_all_categories()


    def get_category_by_id(self,category_id):

        return self.repository.get_category_by_id(category_id)


    def create_category(self,category):
        
        return self.repository.create_category(category)

    
    def update_category(self,category_id,category):

        return self.repository.update_category(category_id,category)

    
    
    def delete_category(self,category_id):
        
        return self.repository.delete_category(category_id)