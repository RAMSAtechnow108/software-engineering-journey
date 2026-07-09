from mysql.connector import Error
from models.student import Student
from exceptions.student_exceptions import StudentNotFoundError
from exceptions.database_exceptions import DatabaseOperationError
from utils.logger import logger


class StudentRepository:

    def __init__(self, connection):
        self.__connection = connection


    def exists_by_email_except_student(self, email, student_id):

        cursor = self.__connection.cursor()

        try:

            query = """
            SELECT 1
            FROM students
            WHERE email = %s
            AND student_id != %s
            LIMIT 1
            """

            cursor.execute(query, (email, student_id))

            row = cursor.fetchone()

            return row is not None

        except Error as error:

            logger.error(
                f"Database error while checking email during update: {error}"
            )

            raise DatabaseOperationError()

        finally:

            cursor.close()


    def exists_by_email(self, email):

        cursor = self.__connection.cursor()

        try:

            query = """
            SELECT 1
            FROM students
            WHERE email = %s
            LIMIT 1
            """

            cursor.execute(query, (email,))

            row = cursor.fetchone()

            return row is not None

        except Error as error:

            logger.error(
                f"Database error while checking email: {error}"
            )

            raise DatabaseOperationError()

        finally:

            cursor.close()


    def add_student(self, student):

        cursor = self.__connection.cursor()

        try:

            query = """
            INSERT INTO students
            (name, age, email, phone, course)
            VALUES
            (%s, %s, %s, %s, %s)
            """

            values = (
                student.name,
                student.age,
                student.email,
                student.phone,
                student.course
            )

            cursor.execute(query, values)

            logger.info(
                f"Student Added | ID={cursor.lastrowid} | Name={student.name}"
            )

        except Error as error:

            logger.error(
                f"Database error while adding student: {error}"
            )

            raise DatabaseOperationError()

        finally:

            cursor.close()


    def __map_row_to_student(self, row):

        return Student(
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5]
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
            FROM students
            """

            cursor.execute(query)

            rows = cursor.fetchall()

            students = []

            for row in rows:
                students.append(
                    self.__map_row_to_student(row)
                )

            return students

        except Error as error:

            logger.error(
                f"Database error while fetching all students: {error}"
            )

            raise DatabaseOperationError()

        finally:

            cursor.close()


    def get_student_by_id(self, student_id):

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
            WHERE student_id = %s
            """

            cursor.execute(query, (student_id,))

            row = cursor.fetchone()

            if row is None:

                logger.error(
                    f"Student Not Found | ID={student_id}"
                )

                raise StudentNotFoundError(student_id)

            return self.__map_row_to_student(row)

        except Error as error:

            logger.error(
                f"Database error while searching student ID={student_id}: {error}"
            )

            raise DatabaseOperationError()

        finally:

            cursor.close()


    def update_student_info(self, student):

        cursor = self.__connection.cursor()

        try:

            query = """
            UPDATE students
            SET
                name = %s,
                age = %s,
                email = %s,
                phone = %s,
                course = %s
            WHERE student_id = %s
            """

            values = (
                student.name,
                student.age,
                student.email,
                student.phone,
                student.course,
                student.student_id
            )

            cursor.execute(query, values)

            logger.info(
                f"Student Updated | ID={student.student_id}"
            )

        except Error as error:

            logger.error(
                f"Database error while updating student ID={student.student_id}: {error}"
            )

            raise DatabaseOperationError()

        finally:

            cursor.close()


    def delete_student(self, student_id):

        cursor = self.__connection.cursor()

        try:

            query = """
            DELETE FROM students
            WHERE student_id = %s
            """

            cursor.execute(query, (student_id,))

            if cursor.rowcount == 0:
                raise StudentNotFoundError(student_id)

            logger.info(
                f"Student Deleted | ID={student_id}"
            )

        except Error as error:

            logger.error(
                f"Database error while deleting student ID={student_id}: {error}"
            )

            raise DatabaseOperationError()

        finally:

            cursor.close()