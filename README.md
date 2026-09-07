# FastAPI Employee Management API
REST API built with FastAPI and Python for managing employee records.

## Features

* User registration
* User login with JWT authentication
* Password hashing with bcrypt
* Protected employee endpoints
* Create employees
* View employees
* Update employees
* Delete employees
* Pagination
* Sorting
* Filtering by department
* Employee search
* File upload support
* SQLite database
* Environment variables for secret configuration

## Technologies Used

* Python
* FastAPI
* SQLAlchemy
* SQLite
* JWT
* Passlib / bcrypt
* Pydantic
* Uvicorn

## API Documentation

FastAPI automatically provides interactive API documentation through Swagger UI.

After starting the application, open:

```text
http://127.0.0.1:8000/docs
```

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/jahnvi2002/employee_api.git
cd employee_api
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn sqlalchemy python-dotenv passlib bcrypt python-jose python-multipart
```

### 4. Create a `.env` file

Add:

```text
SECRET_KEY=your-secret-key
```

### 5. Start the application

```bash
python -m uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Authentication

The API uses JWT bearer tokens.

Users first register and log in. A successful login returns an access token that can be used to access protected employee endpoints.

## Project Structure

```text
employee_api/
├── main.py
├── models.py
├── schemas.py
├── database.py
├── README.md
└── .gitignore
```

## Author

Jahnvi Thareja
