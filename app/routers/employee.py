from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.employee import EmployeeCreate, EmployeeResponse, DeleteResponse
from app.services.employee import (
    create_employees,
    get_employees,
    update_employee,
    delete_employee
)


router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


@router.post("", response_model=list[EmployeeResponse])
def create_employee_endpoint(
    employees: list[EmployeeCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_employees(employees, db)


@router.get("", response_model=list[EmployeeResponse])
def get_employees_endpoint(
    page: int = 1,
    limit: int = 5,
    sort_by: str = "id",
    order: str = "asc",
    department: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_employees(
        page,
        limit,
        sort_by,
        order,
        department,
        search,
        db
    )


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee_endpoint(
    employee_id: int,
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_employee(
        employee_id,
        employee,
        db
    )

@router.delete("/{employee_id}", response_model=DeleteResponse)
def delete_employee_endpoint(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return delete_employee(
        employee_id,
        db
    )