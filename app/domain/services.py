import uuid
from typing import List
from app.utils.exceptions import DomainError
from .repositories import UserRepository, FundRepository, TransactionRepository
from .models import Transaction

class FundsService:
    def __init__(self, users: UserRepository, funds: FundRepository, txs: TransactionRepository):
        self.users = users
        self.funds = funds
        self.txs = txs

    async def list_funds(self):
        return await self.funds.list_all()

    async def subscribe(self, user_id: str, fund_id: str, amount: int) -> Transaction:
        user = await self.users.find_by_id(user_id)
        if not user: raise DomainError("User not found", 404)
        fund = await self.funds.get(fund_id)
        if not fund: raise DomainError("Fund not found", 404)
        if amount < fund.min_amount:
            raise DomainError(f"Monto mínimo de vinculación para {fund.name}: {fund.min_amount}")
        if user.balance < amount:
            raise DomainError(f"No tiene saldo disponible para vincularse al fondo {fund.name}")
        await self.users.update_balance(user.id, user.balance - amount)
        tx = Transaction(
            id=str(uuid.uuid4()),
            user_id=user.id,
            fund_id=fund.id,
            fund_name=fund.name,
            type="SUBSCRIPTION",
            amount=amount,
        )
        await self.txs.create(tx)
        return tx

    async def cancel(self, user_id: str, tx_id: str) -> Transaction:
        user = await self.users.find_by_id(user_id)
        if not user: raise DomainError("User not found", 404)
        history = await self.txs.list_by_user(user.id)
        original = next((t for t in history if t.id == tx_id and t.type == "SUBSCRIPTION"), None)
        if not original:
            raise DomainError("Transacción de suscripción no encontrada", 404)
        await self.users.update_balance(user.id, user.balance + original.amount)
        cancel_tx = Transaction(
            id=str(uuid.uuid4()),
            user_id=user.id,
            fund_id=original.fund_id,
            fund_name=original.fund_name,
            type="CANCELLATION",
            amount=original.amount,
            related_to=original.id,
        )
        await self.txs.create(cancel_tx)
        return cancel_tx

    async def history(self, user_id: str) -> List[Transaction]:
        return await self.txs.list_by_user(user_id)
