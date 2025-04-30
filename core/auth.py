"""
JWT authentication and user dependency utilities.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from authlib.jose import jwt, JoseError
from datetime import datetime, timedelta
from core.config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from core.database import SessionLocal
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode({"alg": JWT_ALGORITHM}, to_encode, JWT_SECRET_KEY).decode()

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY)
        return payload
    except JoseError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_role(role: str):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker
