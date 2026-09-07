from dotenv import load_dotenv
import os
from fastapi import FastAPI, Depends, UploadFile, File as UploadFileType, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from database import SessionLocal, engine
from models import Base, Employee, User
from schemas import EmployeeCreate, UserCreate, UserLogin

load_dotenv()


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".csv",
    ".xlsx",
    ".jpg",
    ".jpeg",
    ".png"
}


Base.metadata.create_all(bind=engine)

app = FastAPI()


# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Database connection
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

# JWT authentication
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(
        User.username == username
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


# HOME
@app.get("/")
def home():
    return {"message": "Employee API is running"}


# REGISTER USER
@app.post("/register")
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user:
        return {"message": "Username already exists"}

    hashed_password = pwd_context.hash(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "username": new_user.username,
        "email": new_user.email
    }

# LOGIN USER
@app.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if existing_user is None:
        return {"message": "Invalid username or password"}

    password_is_correct = pwd_context.verify(
        form_data.password,
        existing_user.hashed_password
    )

    if not password_is_correct:
        return {"message": "Invalid username or password"}

    token_data = {
        "sub": existing_user.username,
        "exp": datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    }

    access_token = jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
         }
         

# CREATE - Add employees
@app.post("/employees")
def create_employees(
    employees: list[EmployeeCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_employees = []

    for employee in employees:

        existing_employee = db.query(Employee).filter(
            Employee.email == employee.email
        ).first()

        if existing_employee:
            raise HTTPException(
                status_code=400,
                detail=f"Employee with email {employee.email} already exists"
            )

        new_employee = Employee(
            name=employee.name,
            email=employee.email,
            department=employee.department
        )

        db.add(new_employee)
        new_employees.append(new_employee)

    db.commit()

    return new_employees


# READ - Get employees with pagination,
# sorting and filtering
@app.get("/employees")
def get_employees(
    page: int = 1,
    limit: int = 5,
    sort_by: str = "id",
    order: str = "asc",
    department: str | None = None,
        search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    skip = (page - 1) * limit

    # Start with all employees
    query = db.query(Employee)

    # Filter by department
    if department:
        query = query.filter(
            Employee.department == department
        )

    # Search by name, email, or department
    if search:
        search_term = f"%{search}%"

        query = query.filter(
            (Employee.name.ilike(search_term)) |
            (Employee.email.ilike(search_term)) |
            (Employee.department.ilike(search_term))
        )

    # Choose sorting column
    if sort_by == "name":
        sort_column = Employee.name
    elif sort_by == "email":
        sort_column = Employee.email
    elif sort_by == "department":
        sort_column = Employee.department
    else:
        sort_column = Employee.id

    # Choose sorting order
    if order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    # Apply sorting and pagination
    employees = (
        query
        .order_by(sort_column)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return employees


# UPDATE - Update one employee
@app.put("/employees/{employee_id}")
def update_employee(
    employee_id: int,
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if existing_employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    existing_employee.name = employee.name
    existing_employee.email = employee.email
    existing_employee.department = employee.department

    db.commit()
    db.refresh(existing_employee)

    return existing_employee

# DELETE - Delete one employee
@app.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    db.delete(employee)
    db.commit()

    return {"message": "Employee deleted successfully"}


# UPLOAD FILE
@app.post("/files/upload")
def upload_file(
    file: UploadFile = UploadFileType(...)
):
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        return {
            "error": "File type not allowed"
        }

    # Create uploads folder if it does not exist
    upload_folder = Path("uploads")
    upload_folder.mkdir(exist_ok=True)

    # Create file path
    file_path = upload_folder / file.filename

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "File uploaded successfully"
    }