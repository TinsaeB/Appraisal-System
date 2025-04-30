"""
Pydantic schemas for User.
"""
from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str
    role: str
    manager_id: Optional[int] = None
    department_id: Optional[int] = None

class UserCreate(UserBase):
    password: str
    manager_id: Optional[int] = None
    department_id: Optional[int] = None

class UserRead(UserBase):
    id: int
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    class Config:
        orm_mode = True
