from database.connection import DatabaseConnection
from models.student import Student
from repositories.student_repository import StudentRepository
from services.student_service import StudentService
from controllers.student_contriller import   StudentController





db = DatabaseConnection()

connection = db.connect()

repo = StudentRepository(connection=connection)

service = StudentService(repository=repo)

controller = StudentController(service=service)
# controller.add_student()


while True:
    
    print("\n" + "="*40)
    print("          Student Management System")
    print("=" *40)


    print("1. Add student")
    print("2. Show Students")
    print("3. Search Student")
    print("4. Update Student")
    print("5. Delete Student")
    print("6. Exit")

    choice = input("\nEnter Choice: ")

    if not choice.isdigit():
        print("Invalid Choice")
        continue
    
    choice  = int(choice) 
    
    if choice == 1:
        controller.add_student()
    
    elif choice == 2:
        controller.show_students()
    
    elif choice == 3:
        controller.search_student()
        
    if choice == 6:
        print("Exiting.....")
        break
        
    
