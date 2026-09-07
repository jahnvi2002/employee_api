from pydantic import BaseModel


class EmployeeCreate(BaseModel):
    name: str
    email: str
    department: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str