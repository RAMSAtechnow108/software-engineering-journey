from database.connection import DatabaseConnection
from repositories.student_repository import StudentRepository
from services.student_service import StudentService
from controllers.student_controller import StudentController
from repositories.audit_repository import AuditRepository




def create_application():
    
    db = DatabaseConnection()

    connection = db.connect()

    repository = StudentRepository(connection)

    audit_repository = AuditRepository(connection)
    
    service = StudentService(repository, audit_repository, connection)

    controller = StudentController(service)
    
    return controller
