from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_db
from app.domain.repositories import UserRepository, FundRepository, TransactionRepository
from app.domain.services import FundsService
from app.domain.schemas import FundOut
from typing import List

router = APIRouter(prefix="/funds", tags=["funds"])

def get_service(db: AsyncIOMotorDatabase) -> FundsService:
    return FundsService(UserRepository(db), FundRepository(db), TransactionRepository(db))

@router.get("", response_model=List[FundOut])
async def list_funds(db: AsyncIOMotorDatabase = Depends(get_db)):
    svc = get_service(db)
    funds = await svc.list_funds()
    return [FundOut(**f.model_dump()) for f in funds]
