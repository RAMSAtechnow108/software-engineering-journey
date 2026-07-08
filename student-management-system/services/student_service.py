from validators.student_validator import StudentValidator
from exceptions.validation_exceptions import DuplicateEmailError
from models.audit_log import AuditLog




class StudentService:
    
    def __init__(self,student_repository,audit_repository ,connection):
        
        self.__student_repository = student_repository
        
        self.__audit_repository = audit_repository
        
        self.__connection  = connection


    def add_student(self,student):

        try:
            StudentValidator.validate_name(student.name) 

            StudentValidator.validate_age(student.age) 
            
            StudentValidator.validate_email(student.email) 
            
            StudentValidator.validate_phone(student.phone) 

            
            if self.__student_repository.exists_by_email(student.email):

                raise DuplicateEmailError()
            
            self.__student_repository.add_student(student)
            
            audit_log = AuditLog(None,f"Student Added: {student.name}")
            
            self.__audit_repository.add_log(audit_log)
    
            self.__connection.commit()
            
        except Exception:

            self.__connection.rollback()

            raise 
        
    def get_all_students(self):

        return self.__student_repository.get_all_students()

    
    
    def get_student_by_id(self,student_id):
        
        return self.__student_repository.get_student_by_id(student_id=student_id)
        
        
    
    
    def update_student(self,student):
            
            
        try:
           
            StudentValidator.validate_name(student.name) 

            StudentValidator.validate_age(student.age) 
            
            StudentValidator.validate_email(student.email) 

            StudentValidator.validate_phone(student.phone) 
            
            if self.__student_repository.exists_by_email_except_student(student.email, student.student_id):
                
                raise DuplicateEmailError()
            
            self.__student_repository.update_student(student=student)
        
            self.__connection.commit()
            
        except Exception:
            
            self.__connection.rollback()
            
            raise
        
    def delete_student(self,student_id):
        
        try:
            
            StudentValidator.validate_id(student_id)
            
            self.__student_repository.delete_student(student_id=student_id)
            
            audit_log = AuditLog(None,f"Student Deleted: {student_id}")
            
            self.__audit_repository.add_log(audit_log)
            
            self.__connection.commit()
        
        except Exception:
            
            self.__connection.rollback()

            raise