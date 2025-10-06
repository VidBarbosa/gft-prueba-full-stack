from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class Fund(BaseModel):
    id: str
    name: str
    min_amount: int
    category: Literal["FPV", "FIC"]

class User(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    password_hash: str
    role: Literal["user", "admin"] = "user"
    balance: int = 500_000
    notify_channel: Literal["email", "sms"] = "email"
    notify_destination: str | None = None

class Transaction(BaseModel):
    id: str
    user_id: str
    fund_id: str
    fund_name: str
    type: Literal["SUBSCRIPTION", "CANCELLATION"]
    amount: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    related_to: Optional[str] = None
