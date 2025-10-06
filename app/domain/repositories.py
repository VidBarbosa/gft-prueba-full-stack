from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from .models import User, Fund, Transaction

USERS = "users"
FUNDS = "funds"
TXS = "transactions"

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase): self.col = db[USERS]
    async def find_by_email(self, email: str) -> Optional[User]:
        doc = await self.col.find_one({"email": email})
        return User(**doc) if doc else None
    async def find_by_id(self, user_id: str) -> Optional[User]:
        doc = await self.col.find_one({"id": user_id})
        return User(**doc) if doc else None
    async def create(self, user: User) -> User:
        await self.col.insert_one(user.model_dump())
        return user
    async def update_balance(self, user_id: str, new_balance: int) -> None:
        await self.col.update_one({"id": user_id}, {"$set": {"balance": new_balance}})

class FundRepository:
    def __init__(self, db: AsyncIOMotorDatabase): self.col = db[FUNDS]
    async def list_all(self) -> List[Fund]:
        cursor = self.col.find({})
        return [Fund(**d) async for d in cursor]
    async def get(self, fund_id: str) -> Optional[Fund]:
        d = await self.col.find_one({"id": fund_id})
        return Fund(**d) if d else None
    async def upsert_many(self, funds: List[Fund]) -> None:
        for f in funds:
            await self.col.update_one({"id": f.id}, {"$set": f.model_dump()}, upsert=True)

class TransactionRepository:
    def __init__(self, db: AsyncIOMotorDatabase): self.col = db[TXS]
    async def create(self, tx: Transaction) -> Transaction:
        await self.col.insert_one(tx.model_dump())
        return tx
    async def list_by_user(self, user_id: str) -> List[Transaction]:
        cursor = self.col.find({"user_id": user_id}).sort("created_at", -1)
        return [Transaction(**d) async for d in cursor]
