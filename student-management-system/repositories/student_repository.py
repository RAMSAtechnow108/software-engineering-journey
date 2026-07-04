from mysql.connector import Error
from models.student import Student


class StudentRepository:
    
    def __init__(self,connection):
        self.__connection = connection
        
    
    def add_student(self, student):
        
        cursor = self.__connection.cursor()

        query = """
        INSERT INTO students
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

    
    
    
    def get_all_students(self):
        cursor = self.__connection.cursor()


        query = """
        SELECT 
            student_id,
            name, 
            age,
            email,
            phone,
            course
        from students
        
        """
        
        cursor.execute(query)

        rows = cursor.fetchall()

        students = []

        for row in rows:
            student = Student(
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5]
            )

            students.append(student)
            
        cursor.close()
        
        return students
        