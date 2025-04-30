"""
App configuration settings.
"""
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./appraisal.db")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day
