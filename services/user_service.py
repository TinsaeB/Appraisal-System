"""
User service: business logic for user management.
"""
from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate
from passlib.hash import bcrypt

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user_in: UserCreate):
    hashed_password = bcrypt.hash(user_in.password)
    user = User(
        username=user_in.username,
        hashed_password=hashed_password,
        role=user_in.role,
        manager_id=user_in.manager_id,
        department_id=user_in.department_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
