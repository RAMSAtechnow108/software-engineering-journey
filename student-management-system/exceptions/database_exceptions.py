from exceptions.base_exception import StudentManagementError


class DatabaseOperationError(StudentManagementError):

    def __init__(self):
        super().__init__(
            "Database operation failed. Please try again later."
        )