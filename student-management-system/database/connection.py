import mysql.connector
from mysql.connector import Error
from exceptions.database_exceptions import DatabaseOperationError
from utils.logger import logger



from config.settings import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_DATABASE
)


class DatabaseConnection:
    
    def __init__(self):
        self.__connection = None
        
    def connect(self):
        
        try:
            
            self.__connection = mysql.connector.connect(
                    host=DB_HOST,
                    port=DB_PORT,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_DATABASE
)
            
            logger.info("Database connection established successfully.")
            return self.__connection
        
        except Error as error:
            logger.error(f"Database connection failed: {error}")
            
            raise DatabaseOperationError()

