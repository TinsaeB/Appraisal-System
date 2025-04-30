"""
Script to seed the database with default departments.
"""
from core.database import SessionLocal, Base, engine
from models.department import Department

def seed_departments():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    departments = [
        {"name": "Finance", "description": "Handles company finances and accounting."},
        {"name": "HR", "description": "Human Resources department."},
        {"name": "Engineering", "description": "Product development and engineering."},
        {"name": "Sales", "description": "Sales and business development."},
        {"name": "Marketing", "description": "Marketing and communications."},
        {"name": "Operations", "description": "Company operations and logistics."},
        {"name": "Management", "description": "Executive and management team."},
    ]
    for dept in departments:
        exists = db.query(Department).filter(Department.name == dept["name"]).first()
        if not exists:
            db.add(Department(**dept))
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_departments()
    print("Seeded default departments.")
