"""
Department model for department management.
"""
from sqlalchemy import Column, Integer, String
from core.database import Base

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
