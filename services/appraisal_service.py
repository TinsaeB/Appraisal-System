"""
Appraisal service: business logic for appraisals.
"""
import os
import shutil
import uuid
from fastapi import UploadFile
from sqlalchemy.orm import Session
from models.appraisal import Appraisal
from schemas.appraisal import AppraisalCreate, AppraisalUpdate
from typing import List, Optional

UPLOAD_DIR = "uploads" # Directory to store attachments

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_upload_file(upload_file: UploadFile) -> str:
    """Saves the uploaded file and returns its unique filename."""
    # Create a unique filename to avoid collisions
    ext = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return unique_filename

def get_attachment_path(filename: str) -> Optional[str]:
    """Returns the full path to the attachment if it exists."""
    file_path = os.path.join(UPLOAD_DIR, filename)
    return file_path if os.path.exists(file_path) else None

def create_appraisal(
    db: Session,
    employee_id: int,
    appraisal_in: AppraisalCreate,
    attachment: Optional[UploadFile] = None
):
    attachment_filename = None
    if attachment:
        # Validate file type (optional but recommended)
        allowed_types = ["application/pdf", "text/csv",
                         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", # Excel .xlsx
                         "application/vnd.ms-excel"] # Excel .xls
        if attachment.content_type not in allowed_types:
            # Consider raising an HTTPException here instead of just returning None
            # For simplicity, we'll just skip saving if type is wrong
            print(f"Invalid file type: {attachment.content_type}") # Log this
        else:
            attachment_filename = save_upload_file(attachment)

    appraisal = Appraisal(
        employee_id=employee_id,
        period=appraisal_in.period,
        self_review=appraisal_in.self_review,
        attachment_filename=attachment_filename, # Save filename
        status="pending"
    )
    db.add(appraisal)
    db.commit()
    db.refresh(appraisal)
    return appraisal

def get_appraisals_by_employee(db: Session, employee_id: int) -> List[Appraisal]:
    return db.query(Appraisal).filter(Appraisal.employee_id == employee_id).all()

def get_appraisals_by_manager(db: Session, manager_id: int) -> List[Appraisal]:
    # Get manager's department
    from models.user import User
    manager = db.query(User).filter(User.id == manager_id, User.role == "Manager").first()
    if not manager or not manager.department_id:
        return []
    # Only employees in same department
    employees = db.query(User).filter(User.department_id == manager.department_id, User.role == "Employee").all()
    employee_ids = [e.id for e in employees]
    return db.query(Appraisal).filter(Appraisal.employee_id.in_(employee_ids)).all()

def get_all_appraisals(db: Session) -> List[Appraisal]:
    return db.query(Appraisal).all()

def update_appraisal(db: Session, appraisal_id: int, appraisal_in: AppraisalUpdate):
    appraisal = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
    if not appraisal:
        return None
    for var, value in vars(appraisal_in).items():
        if value is not None:
            setattr(appraisal, var, value)
    db.commit()
    db.refresh(appraisal)
    return appraisal
