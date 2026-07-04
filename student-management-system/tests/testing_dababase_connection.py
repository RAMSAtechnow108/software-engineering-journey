from database.connection import DatabaseConnection


db = DatabaseConnection()
connection = db.connect()

if connection.is_connected():
    print("Connection Successful.")

