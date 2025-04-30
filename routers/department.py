"""
Router for department management (HR only).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.auth import get_db, require_role
from schemas.department import DepartmentCreate, DepartmentRead
from services.department_service import get_departments, create_department, delete_department
from models.user import User
from typing import List

router = APIRouter(prefix="/departments", tags=["departments"])

@router.get("/", response_model=List[DepartmentRead])
def list_departments(db: Session = Depends(get_db), current_user: User = Depends(require_role("HR"))):
    return get_departments(db)

@router.post("/", response_model=DepartmentRead)
def add_department(dept: DepartmentCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("HR"))):
    return create_department(db, dept)

@router.delete("/{dept_id}")
def remove_department(dept_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("HR"))):
    ok = delete_department(db, dept_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Department not found")
    return {"detail": "Department deleted"}

# Public endpoint for registration page to get department list
@router.get("/public", response_model=List[DepartmentRead])
def public_departments(db: Session = Depends(get_db)):
    return get_departments(db)
