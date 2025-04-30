"""
Appraisal model for employee submissions and manager reviews.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class Appraisal(Base):
    __tablename__ = "appraisals"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"))
    period = Column(String, nullable=False)  # e.g., '2024-Q1'
    self_review = Column(Text)
    manager_review = Column(Text)
    attachment_filename = Column(String, nullable=True) # Store the uploaded file's name
    status = Column(String, default="pending")  # 'pending', 'reviewed', etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    employee = relationship("User", back_populates="appraisals")
