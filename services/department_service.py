"""
Service for department management.
"""
from sqlalchemy.orm import Session
from models.department import Department
from schemas.department import DepartmentCreate
from typing import List

def get_departments(db: Session) -> List[Department]:
    return db.query(Department).all()

def create_department(db: Session, department_in: DepartmentCreate) -> Department:
    department = Department(name=department_in.name, description=department_in.description)
    db.add(department)
    db.commit()
    db.refresh(department)
    return department

def delete_department(db: Session, dept_id: int):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if dept:
        db.delete(dept)
        db.commit()
        return True
    return False
