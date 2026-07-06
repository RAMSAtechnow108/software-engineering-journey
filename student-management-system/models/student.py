class Student:
    
    def __init__(self,student_id, name,age,email,phone,course):
        self.student_id = student_id
        self.name       = name
        self.age        = age
        self.email      = email
        self.phone      = phone
        self.course     = course
        
    
    
    def __str__(self):
        return (
            f"Student("
            f"id={self.student_id},"
            f"name='{self.name}',"
            f"age={self.age},"
            f"email='{self.email}',"
            f"phone={self.phone},"
            f"course='{self.course}',)"
        )
