"""
Authentication and user registration endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from core.auth import get_db, create_access_token
from services.user_service import get_user_by_username, create_user
from schemas.user import UserCreate, UserRead
from passlib.hash import bcrypt

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    user = create_user(db, user_in)
    return user

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not bcrypt.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.id, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}
