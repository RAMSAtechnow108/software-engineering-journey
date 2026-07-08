from exceptions.validation_exceptions import (
    InvalidAgeError,
    InvalidEmailError,
    InvalidIdError,
    InvalidNameError,
    InvalidPhoneError,
)


class StudentValidator:

    @staticmethod
    def validate_name(name):

        if len(name.strip()) < 3:
            raise InvalidNameError()

    @staticmethod
    def validate_age(age):

        if isinstance(age, str):
            if not age.isdigit():
                raise InvalidAgeError()
            age = int(age)

        if age < 18:
            raise InvalidAgeError()

        return age

    @staticmethod
    def validate_email(email):

        if "@" not in email:
            raise InvalidEmailError()

    @staticmethod
    def validate_phone(phone):

        if not phone.isdigit():
            raise InvalidPhoneError()

    @staticmethod
    def validate_id(student_id):

        try:
            student_id = int(student_id)
        except ValueError:
            raise InvalidIdError()
        
        if student_id<=0:
            raise InvalidIdError()
        
        return student_id
        