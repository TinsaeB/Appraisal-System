"""
User model for authentication and role management.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'Employee', 'Manager', 'HR', 'Admin'
    manager_id = Column(Integer)  # Optional: For employees, points to their manager
    department_id = Column(Integer, nullable=True)  # FK to departments.id
    appraisals = relationship("Appraisal", back_populates="employee")
