from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timezone

from database.session import get_db
from api.deps import get_current_user
from models import MLTask, TaskStatus, User
from services.billing import spend_credits_for_predict
from services.rabbitmq import send_to_queue

router = APIRouter(prefix="/predict", tags=["Predictions"])

@router.post("/")
def predict(prompt: str, model_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Проверяем баланс и списываем деньги сразу (предоплата)
    if not spend_credits_for_predict(db, current_user.id):
        raise HTTPException(status_code=402, detail="Insufficient funds")

    # Создаем уникальный ID задачи
    task_id = str(uuid.uuid4())

    # Регистрируем задачу в базе со статусом PROCESSING
    new_task = MLTask(
        id=task_id,
        user_id=current_user.id,
        model_name=model_name,
        prompt=prompt,
        status=TaskStatus.PROCESSING
    )
    db.add(new_task)
    db.commit()

    # Формируем "письмо" для воркера
    message = {
        "task_id": task_id,
        "prompt": prompt,
        "model": model_name
    }

    # Кидаем письмо в RabbitMQ
    send_to_queue(message)

    # Возвращаем клиенту ID задачи. Он потом сможет проверить статус
    return {"task_id": task_id, "status": "Task queued"}