from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.schemas.user import UserCreate, UserLogin
from backend.models.user import User
from backend.utils.security import hash_password, verify_password
from backend.db.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/register")
async def landing():
    return {"message": "Welcome to registration"}

@router.post("/register")
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(User).filter((User.username == user_in.username) | (User.email == user_in.email)))
    existing = q.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "username": user.username, "email": user.email}

@router.get("/login")
async def landing():
    return {"message": "Welcome to login"}

@router.post("/login")
async def login(form_data: UserLogin, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(User).filter(User.email == form_data.email))
    user = q.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"user_id": user.id}
