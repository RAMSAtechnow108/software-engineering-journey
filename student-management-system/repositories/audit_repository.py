from models.audit_log import AuditLog
from utils.logger import logger


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
            
        finally:
            
            cursor.close()
          