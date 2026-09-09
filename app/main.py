from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth
from app.routers import employee
from app.routers import files

# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI()


# Include routers
app.include_router(auth.router)
app.include_router(employee.router)
app.include_router(files.router)


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Employee API is running"
    }