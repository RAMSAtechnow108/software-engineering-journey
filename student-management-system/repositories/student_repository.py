from mysql.connector import Error
from models.student import Student


class StudentRepository:
    
    def __init__(self,connection):
        self.__connection = connection
        
    
    def add_student(self, student):
        
        cursor = self.__connection.cursor()

        query = """
        INSERT INTO TABLE students
        (name,age,email,phone,course)
        VALUES  
        (%s,%s,%s,%s,%s)
        """

        values = (
            student.name,
            student.age,
            student.email,
            student.phone,
            student.course
        )
        

        cursor.execute(query,values)
        
        self.__connection.commit()
        cursor.close()
        print("Student Added Successfully.")

        