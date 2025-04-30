"""
Pydantic schemas for Appraisal.
"""
from pydantic import BaseModel, ConfigDict # Import ConfigDict for Pydantic v2
from typing import Optional
from datetime import datetime

class AppraisalBase(BaseModel):
    period: str
    self_review: Optional[str] = None

class AppraisalCreate(AppraisalBase):
    pass

class AppraisalUpdate(BaseModel):
    self_review: Optional[str] = None
    manager_review: Optional[str] = None
    status: Optional[str] = None
    # Note: We might want an endpoint specifically for adding/updating attachments later

class Appraisal(AppraisalBase): # Renamed from AppraisalRead
    id: int
    employee_id: int
    manager_review: Optional[str]
    attachment_filename: Optional[str] = None # Added field
    status: str
    created_at: datetime
    updated_at: datetime

    # Pydantic V2 uses model_config instead of Config class
    model_config = ConfigDict(from_attributes=True) # Updated Config
