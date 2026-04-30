from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database.session import get_db
from api.deps import get_current_user
from models.user import User
import schemas

router = APIRouter(prefix="/history", tags=["History"])

@router.get("/tasks", response_model=List[schemas.TaskRead])
def get_my_tasks(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Получить историю всех моих ML-задач"""
    # Просто возвращаем список задач из связи, которую мы настроили в моделях
    return current_user.tasks

@router.get("/transactions", response_model=List[schemas.TransactionRead])
def get_my_transactions(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Получить историю моих пополнений и списаний"""
    return current_user.transactions