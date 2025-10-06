from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db import get_db
from app.domain.repositories import UserRepository, FundRepository, TransactionRepository
from app.domain.services import FundsService
from app.domain.schemas import SubscribeIn, TransactionOut
from app.auth import get_current_user_token
from app.utils.notifications import notify
from app.utils.audit import log_event

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

def get_service(db): return FundsService(UserRepository(db), FundRepository(db), TransactionRepository(db))

@router.post("/{fund_id}", response_model=TransactionOut)
async def subscribe(fund_id: str, payload: SubscribeIn, token=Depends(get_current_user_token), db: AsyncIOMotorDatabase = Depends(get_db)):
    svc = get_service(db)
    tx = await svc.subscribe(user_id=token["sub"], fund_id=fund_id, amount=payload.amount)
    user = await UserRepository(db).find_by_id(token["sub"])
    if user and user.notify_destination:
        notify(user.notify_channel, user.notify_destination, "Suscripción creada", f"Te suscribiste a {tx.fund_name} por {tx.amount} COP")
    if user:
        await log_event("SUBSCRIBE", user_id=user.id, actor=user.email, details={"fund_id": tx.fund_id, "fund_name": tx.fund_name, "amount": tx.amount})
    return TransactionOut(id=tx.id, fund_id=tx.fund_id, fund_name=tx.fund_name, type=tx.type, amount=tx.amount)

@router.post("/{transaction_id}/cancel", response_model=TransactionOut)
async def cancel(transaction_id: str, token=Depends(get_current_user_token), db: AsyncIOMotorDatabase = Depends(get_db)):
    svc = get_service(db)
    tx = await svc.cancel(user_id=token["sub"], tx_id=transaction_id)
    user = await UserRepository(db).find_by_id(token["sub"])  # for auditing
    if user:
        await log_event("CANCEL", user_id=user.id, actor=user.email, details={"fund_id": tx.fund_id, "fund_name": tx.fund_name, "amount": tx.amount, "related_to": tx.related_to})
    return TransactionOut(id=tx.id, fund_id=tx.fund_id, fund_name=tx.fund_name, type=tx.type, amount=tx.amount)
