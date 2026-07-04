from services.student_service import StudentService
from models.student import Student


class StudentController:
    
    def __init__(self,service:StudentService):
        self.__service = service
    
    def add_student(self):
        
        name = input("Enter Name: ").capitalize()
        age  = int(input("Enter Age: "))
        email = input("Enter Email: ")
        phone = input("Enter Phone: ")
        course = input("Enter Course: ")

        student = Student(None,name,age, email,phone,course)

        self.__service.add_student(student=student)

    
    def show_students(self):
        
        students =  self.__service.get_all_students()

        if not students :
            print("\nNo students found")
            return
        
        for student in students:
            print(student)