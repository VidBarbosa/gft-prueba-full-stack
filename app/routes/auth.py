from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_db
from app.security import hash_password, verify_password, create_access_token
from app.domain.schemas import RegisterIn, LoginIn, LoginOut, UserOut, UserBasic
from app.domain.models import User
from app.domain.repositories import UserRepository
from app.rate_limit import limiter
from app.utils.audit import log_event
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=201)
@limiter.limit("5/minute")
async def register(request: Request, payload: RegisterIn, db: AsyncIOMotorDatabase = Depends(get_db)):
    users = UserRepository(db)
    existing = await users.find_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        id=str(uuid.uuid4()),
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role="user",
        balance=500_000,
        notify_channel=payload.notify_channel,
        notify_destination=payload.notify_destination or payload.email,
    )
    await users.create(user)
    await log_event("USER_REGISTERED", user.id, actor=user.email, details={"ip": request.client.host})
    return UserOut(**user.model_dump())

@router.post("/login", response_model=LoginOut)
@limiter.limit("30/minute")
async def login(request: Request, payload: LoginIn, db: AsyncIOMotorDatabase = Depends(get_db)):
    users = UserRepository(db)
    user = await users.find_by_email(payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        await log_event("LOGIN_FAILED", user_id=None, actor=payload.email, details={"ip": request.client.host})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(sub=user.id, role=user.role)
    await log_event("LOGIN_SUCCESS", user_id=user.id, actor=user.email, details={"ip": request.client.host})
    return LoginOut(
        access_token=token,
        user=UserBasic(id=user.id, email=user.email, full_name=user.full_name, role=user.role),
    )

@router.post("/logout", status_code=204)
async def logout(request: Request):
    await log_event("LOGOUT", user_id=None, actor=request.client.host, details={})
    return Response(status_code=204)
