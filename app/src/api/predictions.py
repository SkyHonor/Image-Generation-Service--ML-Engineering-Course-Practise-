from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

import schemas
from database.session import get_db
from api.deps import get_current_user
from models.user import User
from models.prediction import MLTask, TaskStatus
from services.billing import spend_credits_for_predict, refund_credits
from services.rabbitmq import send_to_queue
from core.config import settings

router = APIRouter(prefix="/predict", tags=["Predictions"])

@router.post("/", response_model=schemas.TaskRead)
def predict(
    request: schemas.PredictionRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Пытаемся списать кредиты (предоплата)
    if not spend_credits_for_predict(db, current_user.id):
        raise HTTPException(status_code=402, detail="Insufficient funds")

    # Создаем задачу в БД со статусом PROCESSING
    new_task = MLTask(
        user_id=current_user.id,
        model_name=request.model_name,
        prompt=request.prompt,
        status=TaskStatus.PROCESSING
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Пытаемся отправить задачу в RabbitMQ
    try:
        # СТРОГОЕ СООТВЕТСТВИЕ ТЗ: промпт спрятан в словарь features
        message = {
            "task_id": new_task.id,
            "features": {
                "prompt": request.prompt
            },
            "model": request.model_name,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        send_to_queue(message)

    except Exception as e:
        print(f"Ошибка RabbitMQ: {e}")
        # РАББИТ УПАЛ! Делаем возврат средств
        refund_credits(db, current_user.id, settings.PREDICTION_COST)
        
        # Меняем статус задачи на FAILED
        new_task.status = TaskStatus.FAILED
        db.commit()
        
        raise HTTPException(status_code=500, detail="Service temporarily unavailable. Credits refunded.")

    return new_task