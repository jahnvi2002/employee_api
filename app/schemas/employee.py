from pydantic import BaseModel


class EmployeeCreate(BaseModel):
    name: str
    email: str
    department: str

class EmployeeResponse(BaseModel): 
    id: int
    name: str 
    email: str 
    department: str 

    class Config: 
        from_attributes = True

class DeleteResponse(BaseModel):
    message: str