from exceptions.base_exception import StudentManagementError


class InvalidAgeError(StudentManagementError):

    def __init__(self):
        super().__init__("Age must be at least 18.")


class InvalidEmailError(StudentManagementError):

    def __init__(self):
        super().__init__("Invalid email address.")


class InvalidPhoneError(StudentManagementError):

    def __init__(self):
        super().__init__("Phone must contain only digits.")


class InvalidNameError(StudentManagementError):

    def __init__(self):
        super().__init__("Name must contain at least 3 characters.")
        

class InvalidIdError(StudentManagementError):

    def __init__(self):
        super().__init__(
            "Student ID is invalid."
        )