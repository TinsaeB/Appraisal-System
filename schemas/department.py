"""
Pydantic schemas for Department.
"""
from pydantic import BaseModel
from typing import Optional

class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentRead(DepartmentBase):
    id: int
    class Config:
        orm_mode = True
