import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    #Один юзер - один кощелёк (через relationship)
    billing = relationship("BillingAccount", back_populates="owner", uselist=False, cascade="all, delete")
    #Один юзер - много задач
    tasks = relationship("MLTask", back_populates="user")

class BillingAccount(Base):
    __tablename__ = "billing_accounts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    #self.owner_id теперь ForeignKey (связь на уровне БД)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    #self.__balance
    balance = Column(Integer, default=10)

    owner = relationship("User", back_populates="billing")

class MLModel(Base):
    """Новая сущность - доступность модели в системе"""
    __tablename__ = "ml_models"

    id = Column (String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable = False)
    api_key = Column(String, nullable=False)

class MLTask(Base):
    __tablename__ = "ml_tasks"

    id = Column (String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    model_name = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    #self.status
    status = Column(String, default="CREATED")
    #Ссылка на результат из GeneratedImage
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="tasks")