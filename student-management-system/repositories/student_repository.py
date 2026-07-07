from models.student import Student
from exceptions.student_exceptions import StudentNotFoundError
from utils.logger import logger






class StudentRepository:
    
    def __init__(self,connection):
        self.__connection = connection
    
    
    def exists_by_email(self, email):
        
        cursor = self.__connection.cursor()

        try:
            
            query = """
            SELECT 1 FROM students 
            where email=%s
            limit 1
            """
            
            cursor.execute(query,(email,))
            row = cursor.fetchone()
            
            return row is not None
            
        
        finally:
            
            cursor.close()
    
    def add_student(self, student):
        
        cursor = self.__connection.cursor()

        try:
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
            
            logger.info(f"Student Added | ID={cursor.lastrowid} | Name={student.name}")
            
            
        finally:
            cursor.close()

    
    def __map_row_to_student(self,row):
        return Student(
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            )
    
    
    def get_all_students(self):
        cursor = self.__connection.cursor()

        
        try:
            
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
                students.append( self.__map_row_to_student(row))
           
            return students
        
        finally: 

            cursor.close()
            
            
        
    def get_student_by_id(self,student_id):
        
        cursor = self.__connection.cursor()

        try:
            query = """
            SELECT 
                student_id,
                name,
                age,
                email,
                phone,
                course
            FROM students
            WHERE student_id=%s
            """
            
            cursor.execute(query,(student_id,))

            row = cursor.fetchone()
            
            if row is None:
                logger.error(f"Student Not Found | ID={student_id}")
                raise StudentNotFoundError(student_id)
            
            student = self.__map_row_to_student(row)
            
            return student
        
        finally:
            
            cursor.close()
        
    def update_student_info(self,student):
        
        cursor = self.__connection.cursor()

        
        try:
            query = """
            UPDATE students
            set 
                name = %s,
                age = %s,
                email = %s,
                phone = %s,
                course = %s
            where student_id = %s
            """
            
            values = (
                student.name,
                student.age,
                student.email,
                student.phone,
                student.course,
                student.student_id
            )
            
            cursor.execute(query,values)

            self.__connection.commit()
            
            logger.info(f"Student Updated | ID={student.student_id}")

        finally:
            cursor.close()


        
        
    def delete_student(self,student_id):
        
        cursor = self.__connection.cursor()
        try:
            query = """
            DELETE from students
            WHERE student_id=%s
            """
            
            
            cursor.execute(query,(student_id,))

            self.__connection.commit()
            
            logger.info(f"Student Deleted | ID={student_id}")

        finally:
            cursor.close()

