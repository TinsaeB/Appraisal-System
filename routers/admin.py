"""
Admin endpoints for user management and profile viewing.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.auth import get_db, require_role, get_current_user
from schemas.user import UserRead
from models.user import User
from typing import List

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=List[UserRead])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_role("Admin"))):
    return db.query(User).all()

@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("Admin"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_in: UserRead, db: Session = Depends(get_db), current_user: User = Depends(require_role("Admin"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for var, value in user_in.dict(exclude_unset=True).items():
        setattr(user, var, value)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("Admin"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}

# Profile endpoint for any user
@router.get("/profile", response_model=UserRead)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
