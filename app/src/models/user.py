import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # Связи (relationships)
    billing = relationship("BillingAccount", back_populates="owner", uselist=False, cascade="all, delete")
    tasks = relationship("MLTask", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")