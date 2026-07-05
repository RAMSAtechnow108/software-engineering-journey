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
        
    
    def search_student(self):
        
        student_id = input("Enter Student ID: ")

        if not student_id.isdigit():
            print("Please enter valid id ")
            return 
        
        student = self.__service.get_student_by_id(student_id)
        
        student.course="java"
        print(student)


    def update_student(self):
        student_id = input("Enter Student ID: ")
        if not student_id.isdigit():
            print("Invalid input")
            return 
        
        student = self.__service.get_student_by_id(student_id=student_id)
        
        if student is None:
            print("Student not found")
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

        self.__service.update_student(student)
        