from repositories.student_repository import StudentRepository
from validators.student_validator import StudentValidator
from exceptions.validation_exceptions import DuplicateEmailError


class StudentService:
    
    def __init__(self,repository: StudentRepository):
        self.__repository = repository


    def add_student(self,student):
        
        StudentValidator.validate_name(student.name) 

        StudentValidator.validate_age(student.age) 
        
        StudentValidator.validate_email(student.email) 
        
        StudentValidator.validate_phone(student.phone) 

        
        if self.__repository.exists_by_email(student.email):

            raise DuplicateEmailError()
        
        self.__repository.add_student(student=student)
        
        
    def get_all_students(self):

        return self.__repository.get_all_students()

    
    
    def get_student_by_id(self,student_id):
        
        student = self.__repository.get_student_by_id(student_id=student_id)
        
        return student
    
    
    def update_student(self,student):
        
        StudentValidator.validate_name(student.name) 

        StudentValidator.validate_age(student.age) 
        
        StudentValidator.validate_email(student.email) 

        StudentValidator.validate_phone(student.phone) 
        
        if self.__repository.exists_by_email_except_student(student.email, student.student_id):
            
            raise DuplicateEmailError()
        
        self.__repository.update_student_info(student=student)
        
        
    def delete_student(self,student_id):
        
        StudentValidator.validate_id(student_id)
        self.__repository.delete_student(student_id=student_id)
        