from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models import TaskStatus, TransactionType

# Схемы для пользователя
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: str
    username: str
    email: EmailStr
    class Config:
        from_attributes = True

# Схемы для баланса
class BalanceRead(BaseModel):
    balance: int

class DepositRequest(BaseModel):
    user_id: str
    amount: int

# Схемы для ML задач
class PredictionRequest(BaseModel):
    user_id: str
    model_name: str
    prompt: str

class TaskRead(BaseModel):
    id: str
    model_name: str
    prompt: str
    status: TaskStatus
    image_url: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

# Схемы для транзакций
class TransactionRead(BaseModel):
    id: str
    amount: int
    transaction_type: TransactionType
    created_at: datetime
    class Config:
        from_attributes = True