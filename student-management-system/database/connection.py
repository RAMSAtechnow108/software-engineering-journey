import mysql.connector
from mysql.connector import Error



from config.settings import (
    HOST,
    PORT, 
    USER,
    PASSWORD,
    DATABASE
    )


class DatabaseConnection:
    
    def __init__(self):
        self.__connection = None
        
    def connect(self):
        
        try:
            
            self.__connection = mysql.connector.connect(
                host = HOST,
                port =PORT,
                user = USER,
                password  = PASSWORD,
                database = DATABASE
            )

            return self.__connection
        
        except Error as error:
            print(error)

