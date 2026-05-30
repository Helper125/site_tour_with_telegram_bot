from .models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from fastapi import HTTPException
from .schemas import Register, Login
from .hashing import hash_password, verify_password, create_token

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: Register):
        existing = await self.db.scalar(select(User).where(User.email == data.email or User.username == data.username))
        if existing:
            raise HTTPException(status_code=400, detail="Email or username already extist.")

        reg = User(username=data.username, email=data.email, password=hash_password(data.password))
        self.db.add(reg)
        await self.db.flush()
        return create_token(reg.id)
    

    async def login(self, data: Login):
        existing = await self.db.scalar(select(User).where(User.email == data.email))
        if not existing:
            raise HTTPException(status_code=400, detail="This account does not exist.")
        
        if not verify_password(data.password, existing.password):
            raise HTTPException(status_code=404, detail="Incorrect email or password.")
        
        return create_token(existing.id)