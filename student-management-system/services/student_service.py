from repositories.student_repository import StudentRepository



class StudentService:
    
    def __init__(self,repository: StudentRepository):
        self.__repository = repository


    def add_student(self,student):
        
        if student.age<18:
            print("Student age must be at least 18")
            return 
    
        self.__repository.add_student(student=student)