from bootstrap.application import create_application
from exceptions.database_exceptions import DatabaseOperationError


try:
    
    controller = create_application()

except DatabaseOperationError as error:
    print(error)
    exit()


while True:
    
    print("\n" + "="*40)
    print("          Student Management System")
    print("=" *40)


    print("1. Add student")
    print("2. Show Students")
    print("3. Search Student")
    print("4. Update Student")
    print("5. Delete Student")
    print("6. Exit")

    choice = input("\nEnter Choice: ").strip()

    if not choice.isdigit():
        print("Invalid Choice")
        continue
    
    choice  = int(choice) 
    
    if choice == 1:
        controller.add_student()
    
    elif choice == 2:
        controller.show_students()
    
    elif choice == 3:
        controller.search_student()
    
    elif choice == 4:
        controller.update_student()
        
    elif choice == 5:
        controller.delete_student()
    if choice == 6:
        print("Exiting.....")
        break
        
    