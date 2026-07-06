class StudentValidator:
    
    @staticmethod
    def validate_age(age):
        
        if age<18:
            raise ValueError("Age must be at least 18.")



    @staticmethod
    def validate_phone(phone):
        
        if not phone.isdigit():
            raise ValueError("Phone must contain only digits.")

    
    
    @staticmethod
    def validate_email(email):
        
        if "@" not in email:
            raise ValueError("Invalid email address.")

    
    @staticmethod
    def validate_name(name):
        if len(name.strip()) <3:
            raise ValueError("Name is too short.")
    
    