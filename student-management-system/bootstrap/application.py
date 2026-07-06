from database.connection import DatabaseConnection
from repositories.student_repository import StudentRepository
from services.student_service import StudentService
from controllers.student_controller import StudentController



def create_application():
    
    db = DatabaseConnection()

    connection = db.connect()

    repository = StudentRepository(connection)

    service = StudentService(repository)

    controller = StudentController(service)
    
    return controller
