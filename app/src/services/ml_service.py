from sqlalchemy.orm import Session
from models.prediction import MLTask, TaskStatus
from services.billing import spend_credits_for_predict

def create_prediction_task(db: Session, user_id: str, model_name: str, prompt: str):
    # 1. Пытаемся списать деньги
    if not spend_credits_for_predict(db, user_id):
        return None 
    
    # Создаем задачу
    new_task = MLTask(
        user_id=user_id,
        model_name=model_name,
        prompt=prompt,
        status=TaskStatus.COMPLETED,
        image_url="https://storage.googleapis.com/fake-bucket/generated.png"
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return new_task