from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate


def create_employees(
    employees: list[EmployeeCreate],
    db: Session
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


def get_employees(
    page: int,
    limit: int,
    sort_by: str,
    order: str,
    department: str | None,
    search: str | None,
    db: Session
):
    skip = (page - 1) * limit

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

    employees = (
        query
        .order_by(sort_column)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return employees


def update_employee(
    employee_id: int,
    employee: EmployeeCreate,
    db: Session
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


def delete_employee(
    employee_id: int,
    db: Session
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

    return {
        "message": "Employee deleted successfully"
    }