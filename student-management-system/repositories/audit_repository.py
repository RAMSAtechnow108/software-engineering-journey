from models.audit_log import AuditLog
from utils.logger import logger
from mysql.connector import Error
from exceptions.database_exceptions import DatabaseOperationError



class AuditRepository():
    
    def __init__(self,connection):
        self.__connection = connection
        

    def add_log(self,audit_log):
        
        cursor = self.__connection.cursor()
        
        try:   
            
            query = """
            INSERT INTO audit_logs
            (action)
            values
            (%s)
            """
            
            cursor.execute(query,(audit_log.action,))
            

            logger.info(f"Audit Log Added | {audit_log.action}")
            
        except Error as error:

            logger.error(
                f"Database error while adding audit log: {error}"
            )

            raise DatabaseOperationError()
        
        finally:
            
            cursor.close()
          