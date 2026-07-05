from repositories.student_repository import StudentRepository



class StudentService:
    
    def __init__(self,repository: StudentRepository):
        self.__repository = repository


    def add_student(self,student):
        
        if student.age<18:
            print("Student age must be at least 18")
            return 
    
        self.__repository.add_student(student=student)
        
    def get_all_students(self):

        student = self.__repository.get_all_students()

        return student
    
    
    def get_student_by_id(self,student_id):
        
        student = self.__repository.get_student_by_id(student_id=student_id)
        
        return student
    
    
    def update_student(self,student):
        if student.age < 18:
            print("Student age must be at least 18")
            return 
        
        self.__repository.update_student_info(student=student)