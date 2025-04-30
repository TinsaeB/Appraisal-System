"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from core.database import Base, engine
from routers import auth, appraisal, hr, admin, department

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Appraisal Reporting System")

# Register routers
app.include_router(auth.router)
app.include_router(appraisal.router)
app.include_router(hr.router)
app.include_router(admin.router)
app.include_router(department.router)
