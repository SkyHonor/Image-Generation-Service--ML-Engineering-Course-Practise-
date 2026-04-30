import uuid
import enum
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum as SQLAEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base

class TaskStatus(enum.Enum):
    CREATED = "created"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class MLModel(Base):
    __tablename__ = "ml_models"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False)

class MLTask(Base):
    __tablename__ = "ml_tasks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    model_name = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    status = Column(SQLAEnum(TaskStatus), default=TaskStatus.CREATED)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user = relationship("User", back_populates="tasks")