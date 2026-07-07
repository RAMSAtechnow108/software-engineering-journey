from exceptions.base_exception import StudentManagementError


class StudentNotFoundError(StudentManagementError):

    def __init__(self, student_id):
        super().__init__(
            f"Student with ID {student_id} not found."
        )