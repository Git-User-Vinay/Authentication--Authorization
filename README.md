# FastAPI JWT Authentication Example

This project demonstrates a simple user authentication system using FastAPI, JWT, and Tortoise ORM. It supports user registration, login (token generation), and access to the authenticated user's data.

## Features

- User registration with password hashing.
- User login with JWT token generation.
- Token-based authentication to access user-specific information.
- PostgreSQL database integration using Tortoise ORM.
  
## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.8+
- PostgreSQL (or any other compatible database)

### Step 1: Clone the repository

git clone https://github.com/Git-User-Vinay/Authentication--Authorization.git
cd fastapi-jwt-auth
 
### Step 2: Create a virtual environment

python -m venv venv

### Step 3: Activate the virtual environment

venv\Scripts\activate

### Step 4: Set up the database
Ensure you have PostgreSQL installed and running on your machine. Create a new database named auth_db.

CREATE DATABASE auth_db;

### Step 5: Configure the database URL
In the main.py file, ensure the register_tortoise function is configured with the correct database URL:

register_tortoise(
    app,
    db_url='postgres://postgres:1234@localhost:5432/auth_db',  
    modules={'models': ['main']},
    generate_schemas=True,
    add_exception_handlers=True
)
Change postgres:1234 to your PostgreSQL username and password if they differ.

### Step 6 Run the application

hypercorn main:app --reload
