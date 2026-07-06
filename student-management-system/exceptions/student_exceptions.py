class StudentNotFoundError(Exception):
    
    def __init__(self, student_id):
        self.student_id = student_id
        
        super().__init__(f"Student with ID {student_id} not found.")
        
        
class 