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
            student.course
        )
