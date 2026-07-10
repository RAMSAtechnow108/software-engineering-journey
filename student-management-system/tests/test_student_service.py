import pytest

from unittest.mock import Mock

from services.student_service import StudentService
from models.student import Student
from exceptions.validation_exceptions import DuplicateEmailError


def test_duplicate_email_does_not_add_student():
    
    student_repository = Mock()
    audit_repository = Mock()
    connection = Mock()

    service = StudentService(student_repository, audit_repository, connection)

    student = Student(None, "Rahul","21","rahul@gmail.com","3453532534","Python")
    
    student_repository.exists_by_email.return_value = True

    with pytest.raises(DuplicateEmailError):
        service.add_student(student)
    
    
    student_repository.add_student.assert_not_called()
    audit_repository.add_log.assert_not_called()
    connection.commit.assert_not_called()
    connection.rollback.assert_called_once()
    

def test_add_student_successfully():

    student_repository = Mock()
    audit_repository = Mock()
    connection = Mock()

    service = StudentService(
        student_repository,
        audit_repository,
        connection
    )

    student = Student(
        None,
        "Rahul",
        "21",
        "rahul@gmail.com",
        "9876543210",
        "Python"
    )

    student_repository.exists_by_email.return_value = False

    service.add_student(student)

    # Ab assertions tum likho
    student_repository.add_student.assert_called_with(student)
    audit_repository.add_log.assert_called_once()
    connection.commit.assert_called_once()
    connection.rollback.assert_not_called()
    
def test_add_student_rolls_back_when_audit_fails():

    student_repository = Mock()
    audit_repository = Mock()
    connection = Mock()

    service = StudentService(
        student_repository,
        audit_repository,
        connection
    )

    student = Student(
        None,
        "Rahul",
        "21",
        "rahul@gmail.com",
        "9876543210",
        "Python"
    )

    student_repository.exists_by_email.return_value = False

    audit_repository.add_log.side_effect = Exception("Audit failed")

    with pytest.raises(Exception):
        service.add_student(student)

    student_repository.add_student.assert_called_once_with(student)

    audit_repository.add_log.assert_called_once()

    connection.commit.assert_not_called()

    connection.rollback.assert_called_once()