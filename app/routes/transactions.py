from typing import List
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_db
from app.domain.repositories import UserRepository, FundRepository, TransactionRepository
from app.domain.services import FundsService
from app.domain.schemas import TransactionOut, TransactionsList
from app.auth import get_current_user_token

router = APIRouter(prefix="/transactions", tags=["transactions"])

def get_service(db): return FundsService(UserRepository(db), FundRepository(db), TransactionRepository(db))

@router.get("", response_model=TransactionsList)
async def history(token=Depends(get_current_user_token), db: AsyncIOMotorDatabase = Depends(get_db)):
    svc = get_service(db)
    txs = await svc.history(user_id=token["sub"])
    items = [TransactionOut(id=t.id, fund_id=t.fund_id, fund_name=t.fund_name, type=t.type, amount=t.amount) for t in txs]
    return TransactionsList(items=items)
