"""
Endpoints for employee and manager appraisal operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File # Added UploadFile, File
from fastapi.responses import FileResponse # To return files
from sqlalchemy.orm import Session
from core.auth import get_db, get_current_user, require_role
from schemas.appraisal import AppraisalCreate, Appraisal, AppraisalUpdate
from services.appraisal_service import (
    create_appraisal, get_appraisals_by_employee, get_appraisals_by_manager, update_appraisal, get_attachment_path # Added get_attachment_path
)
from models.user import User
from typing import List, Optional # Added Optional

router = APIRouter(prefix="/appraisals", tags=["appraisals"])

# Any logged-in user: Create appraisal with optional attachment
@router.post("/", response_model=Appraisal)
def submit_appraisal(
    # Use Form data because we have a file upload
    period: str = File(...),
    self_review: Optional[str] = File(None),
    attachment: Optional[UploadFile] = File(None), # Accept file upload
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Allow any logged-in user
):
    # Create the schema object from Form data
    appraisal_in = AppraisalCreate(period=period, self_review=self_review)
    return create_appraisal(db, current_user.id, appraisal_in, attachment) # Pass attachment

@router.get("/my", response_model=List[Appraisal])
def list_my_appraisals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_appraisals_by_employee(db, current_user.id)

# Endpoint to download an attachment
@router.get("/{appraisal_id}/attachment")
def download_attachment(
    appraisal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Check permissions below
):
    appraisal = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
    if not appraisal:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    if not appraisal.attachment_filename:
        raise HTTPException(status_code=404, detail="No attachment found for this appraisal")

    # Permission check: Allow owner, their manager, or HR/Admin
    is_owner = appraisal.employee_id == current_user.id
    is_manager = current_user.role == "Manager" and appraisal.employee.department_id == current_user.department_id # Simplified check
    is_hr_or_admin = current_user.role in ["HR", "Admin"]

    if not (is_owner or is_manager or is_hr_or_admin):
         raise HTTPException(status_code=403, detail="Not authorized to view this attachment")

    file_path = get_attachment_path(appraisal.attachment_filename)
    if not file_path:
        raise HTTPException(status_code=404, detail="Attachment file not found on server")

    return FileResponse(path=file_path, filename=appraisal.attachment_filename)


# Manager: View and comment on appraisals of employees under them
from fastapi import Query

@router.get("/team", response_model=List[Appraisal]) # Changed AppraisalRead to Appraisal
def list_team_appraisals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Manager"))
):
    return get_appraisals_by_manager(db, current_user.id)

@router.get("/team/report")
def team_report(
    format: str = Query("pdf", enum=["pdf", "json"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Manager"))
):
    from services.appraisal_service import get_appraisals_by_manager
    appraisals = get_appraisals_by_manager(db, current_user.id)
    if not appraisals:
        raise HTTPException(status_code=404, detail="No appraisals found for your team")
    if format == "json":
        # Use the already imported Appraisal schema
        return [Appraisal.model_validate(a) for a in appraisals]
    from utils.pdf import generate_appraisal_pdf
    pdf_bytes = generate_appraisal_pdf(appraisals)
    return Response(pdf_bytes, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=team_appraisal_report.pdf"
    })

@router.patch("/{appraisal_id}", response_model=Appraisal) # Changed AppraisalRead to Appraisal
def review_appraisal(
    appraisal_id: int,
    appraisal_in: AppraisalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Manager"))
):
    updated = update_appraisal(db, appraisal_id, appraisal_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    return updated
