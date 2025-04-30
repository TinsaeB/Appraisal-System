"""
Endpoints for HR to view all appraisals and generate PDF reports.
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from core.auth import get_db, require_role
from services.appraisal_service import get_all_appraisals
from schemas.appraisal import Appraisal # Changed AppraisalRead to Appraisal
from models.user import User
from utils.pdf import generate_appraisal_pdf
from typing import List

router = APIRouter(prefix="/hr", tags=["hr"])

@router.get("/appraisals", response_model=List[Appraisal]) # Changed AppraisalRead to Appraisal
def list_all_appraisals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("HR"))
):
    return get_all_appraisals(db)

from fastapi import Query

@router.get("/appraisals/{employee_id}/report")
def generate_report(
    employee_id: int,
    format: str = Query("pdf", enum=["pdf", "json"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("HR"))
):
    from services.appraisal_service import get_appraisals_by_employee
    appraisals = get_appraisals_by_employee(db, employee_id)
    if not appraisals:
        raise HTTPException(status_code=404, detail="No appraisals found for employee")
    if format == "json":
        # Use the already imported Appraisal schema
        return [Appraisal.model_validate(a) for a in appraisals]
    pdf_bytes = generate_appraisal_pdf(appraisals)
    return Response(pdf_bytes, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=employee_{employee_id}_appraisal_report.pdf"
    })
