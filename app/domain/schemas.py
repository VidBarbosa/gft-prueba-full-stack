from typing import Literal, Optional, List
from pydantic import BaseModel, EmailStr, Field

class RegisterIn(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    notify_channel: Literal["email", "sms"] = "email"
    notify_destination: Optional[str] = None

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserBasic(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str

class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserBasic

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    balance: int
    notify_channel: str
    notify_destination: Optional[str] = None

class FundOut(BaseModel):
    id: str
    name: str
    min_amount: int
    category: str

class SubscribeIn(BaseModel):
    amount: int = Field(gt=0)

class TransactionOut(BaseModel):
    id: str
    fund_id: str
    fund_name: str
    type: str
    amount: int

class TransactionsList(BaseModel):
    items: List[TransactionOut]
