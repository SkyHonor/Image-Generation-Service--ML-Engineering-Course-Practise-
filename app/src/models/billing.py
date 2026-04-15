import uuid
import enum
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum as SQLAEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base

class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"

class BillingAccount(Base):
    __tablename__ = "billing_accounts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    balance = Column(Integer, default=10)
    owner = relationship("User", back_populates="billing")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    transaction_type = Column(SQLAEnum(TransactionType), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user = relationship("User", back_populates="transactions")