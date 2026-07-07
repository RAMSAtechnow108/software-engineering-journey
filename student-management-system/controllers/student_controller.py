from services.student_service import StudentService
from models.student import Student
from exceptions.student_exceptions import StudentManagementError
from utils.logger import logger



class StudentController:
    
    def __init__(self,service:StudentService):
        self.__service = service
    
    
    
    
    
    
    def add_student(self):
        
        logger.info("Add Student Request Received")

        name = input("Enter Name: ").capitalize()
        age  = (input("Enter Age: "))
        email = input("Enter Email: ")
        phone = input("Enter Phone: ")
        course = input("Enter Course: ").capitalize()

        student = Student(None,name,age, email,phone,course)

        try:
            
            self.__service.add_student(student=student)

            print("Student Added Successfully.")
            
        except StudentManagementError as e:
            print(e)






    
    def show_students(self):
        
        logger.info("All Student Show Request")
        students =  self.__service.get_all_students()

        if not students :
            print("\nNo students found")
            return
        
        for student in students:
            print(student)
        


        
    
    def search_student(self):
        
        student_id = input("Enter Student ID: ")
        
        logger.info(f"Search Student Request | ID={student_id}")

         
        try:
            
            student = self.__service.get_student_by_id(student_id)
        
        except StudentManagementError as error:
            print(error)
            return
        
        
        print(student)












    def update_student(self):
        student_id = input("Enter Student ID: ")
         
        logger.info(F"Update Student Request | ID={student_id}")
        
        try : 
            
            student = self.__service.get_student_by_id(student_id=student_id)
            
            
        except StudentManagementError as e:
            print(e)
            return      

        print(student)
        
        
        new_name = input(f"Current Name: {student.name}\nEnter New Name (Press Enter to keep current): ")
        if new_name:
            student.name = new_name

        new_age = input(f"Current Age: {student.age}\nEnter New Age (Press Enter to keep current): ")
        if new_age:
            if not new_age.isdigit():
                print("Invalid age")
                return
            student.age = int(new_age)

        new_email = input(f"Current Email: {student.email}\nEnter New Email (Press Enter to keep current): ")
        if new_email:
            student.email = new_email

        new_phone = input(f"Current Phone: {student.phone}\nEnter New Phone (Press Enter to keep current): ")
        if new_phone:
            student.phone = new_phone

        new_course = input(f"Current Course: {student.course}\nEnter New Course (Press Enter to keep current): ")
        if new_course:
            student.course = new_course

        try:
            self.__service.update_student(student)
            print(f"Student details succesffully updated.")
        except ValueError as e:
            print(e)
        
        
    
    
    
    
    
    
    
    
    def delete_student(self):
        
        student_id = input("Enter student ID: ")
        
        logger.info(f"Delete Student Request | ID={student_id}")
        
        if not student_id.isdigit():
            print("Invalid student ID")
            return 
        
        student_id = int(student_id)


        try:
            
            student = self.__service.get_student_by_id(student_id=student_id)
        
        except StudentManagementError as e:
            print(e)
            
            return 
        print(student) 
        
        choice = input("Are you sure? (Y/N): ").lower()

        if choice == "y":
            self.__service.delete_student(student_id)

            print("Student Deleted Successfully.")

        else:
            
            print("Delete Cancelled")

        

        