from database.connection import DatabaseConnection
from models.student import Student
from repositories.student_repository import StudentRepository
from services.student_service import StudentService
from controllers.student_contriller import   StudentController



db = DatabaseConnection()

connection = db.connect()

if connection.is_connected():
    print("Successfully ")
repo = StudentRepository(connection=connection)

student1 = Student(None,"Rahul",20,"rahul@gmail.com","9876543210","Python")

repo = repo.add_student(student=student1)
