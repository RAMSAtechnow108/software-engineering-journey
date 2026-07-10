# Student Management System

A command-line based Student Management System built with Python and MySQL to practice real backend engineering concepts such as layered architecture, repository pattern, service layer, validation, custom exceptions, dependency injection, logging, database transactions, audit logs, and automated testing.

## Features

* Add a new student
* View all students
* Search student by ID
* Update student information
* Delete student with confirmation
* Validate student name, age, email, phone, and ID
* Prevent duplicate email addresses
* Custom exception handling
* Graceful database error handling
* Application logging
* Audit logging for important operations
* Transaction management with commit and rollback
* Environment-based database configuration
* Automated unit testing with pytest and mocks

## Architecture

The application follows a layered architecture:

```text
main.py
   |
   v
Controller
   |
   v
Service
   |
   +--------------------+
   |                    |
   v                    v
StudentRepository   AuditRepository
   |                    |
   +---------+----------+
             |
             v
           MySQL
```

### Layer Responsibilities

**Controller Layer**

* Receives user input
* Displays output
* Calls the service layer

**Service Layer**

* Handles business logic
* Coordinates repositories
* Manages transactions
* Performs commit and rollback

**Repository Layer**

* Executes SQL queries
* Converts database rows into model objects
* Does not control transactions

**Validator Layer**

* Validates student data
* Raises custom validation exceptions

**Model Layer**

* Represents application entities such as `Student` and `AuditLog`

## Project Structure

```text
student-management-system/
|
├── bootstrap/
│   └── application.py
|
├── config/
│   └── settings.py
|
├── controllers/
│   └── student_controller.py
|
├── database/
│   └── connection.py
|
├── exceptions/
│   ├── base_exception.py
│   ├── database_exceptions.py
│   ├── student_exceptions.py
│   └── validation_exceptions.py
|
├── models/
│   ├── student.py
│   └── audit_log.py
|
├── repositories/
│   ├── student_repository.py
│   └── audit_repository.py
|
├── services/
│   └── student_service.py
|
├── tests/
│   ├── test_student_service.py
│   └── test_student_validator.py
|
├── utils/
│   └── logger.py
|
├── validators/
│   └── student_validator.py
|
├── .env.example
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## Technologies Used

* Python 3
* MySQL
* mysql-connector-python
* python-dotenv
* pytest
* unittest.mock
* Git and GitHub

## Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd student-management-system
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the project root using `.env.example` as a reference:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_database_password
DB_DATABASE=student_management_db
```

Never commit the real `.env` file because it may contain sensitive credentials.

## Database Setup

Create the database:

```sql
CREATE DATABASE student_management_db;
```

Create the students table:

```sql
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    course VARCHAR(100) NOT NULL
);
```

Create the audit logs table:

```sql
CREATE TABLE audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Run the Application

```bash
python main.py
```

The CLI menu provides these operations:

```text
========================================
          Student Management System
========================================
1. Add student
2. Show Students
3. Search Student
4. Update Student
5. Delete Student
6. Exit
```

## Transaction Management

Important database operations are executed inside transactions.

For example, when adding a student:

```text
Validate Student
      |
      v
Check Duplicate Email
      |
      v
Insert Student
      |
      v
Insert Audit Log
      |
      +---- Success ----> COMMIT
      |
      +---- Failure ----> ROLLBACK
```

This ensures atomicity: either all related operations succeed together, or all of them are rolled back.

## Error Handling

The project uses custom exception classes for:

* Invalid name
* Invalid age
* Invalid email
* Invalid phone
* Invalid student ID
* Duplicate email
* Student not found
* Database operation failures

Technical database errors are written to logs, while users receive clean messages such as:

```text
Database operation failed. Please try again later.
```

## Testing

Run all automated tests:

```bash
python -m pytest -v
```

The current test suite covers:

* Valid age validation
* Invalid age exception handling
* Non-numeric age input
* Duplicate email behavior
* Successful student creation
* Transaction rollback when audit logging fails

Testing concepts used:

* `pytest`
* `pytest.raises()`
* `Mock`
* `return_value`
* `side_effect`
* `assert_called_once()`
* `assert_called_once_with()`
* `assert_not_called()`

## Backend Engineering Concepts Practiced

This project was built to practice:

* Object-Oriented Programming
* Layered Architecture
* Repository Pattern
* Service Layer
* Controller Layer
* Dependency Injection
* Business Logic Separation
* Single Responsibility Principle basics
* Custom Exception Hierarchy
* Exception Propagation
* Validation Layer
* Logging
* Environment Variables
* Database Transactions
* Commit and Rollback
* Transaction Atomicity
* Audit Logging
* Unit Testing
* Mocking
* Git and GitHub workflow

## Project Status

Completed as a backend engineering learning project.

The focus of this project was not only CRUD operations, but understanding how different backend layers collaborate, how failures propagate through the application, and how transactions protect data consistency.
