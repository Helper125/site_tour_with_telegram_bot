from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.dependency import get_db
from .models import User
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY_JWT")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["argon2"])
security = HTTPBearer()

def hash_password(password):
    hashing = pwd_context.hash(password)
    return hashing

def verify_password(password, hash_password):
    veryfing = pwd_context.verify(password, hash_password)
    return veryfing

def create_token(user_id: int):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id")
    
    except Exception as e:
        print("JWT ERROR:", e)
        return None

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("token")
    if not token:
        return None
    
    user_id = decode_token(token)
    user = await db.get(User, user_id)

    if not user:
        return None
    return user