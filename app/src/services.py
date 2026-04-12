from sqlalchemy.orm import Session
from models import User, BillingAccount, MLTask, MLModel
from datetime import datetime, timezone

#Пополнение баланса
def add_credits(db: Session, user_id: str, amount: int):
    billing = db.query(BillingAccount).filter(BillingAccount.user_id == user_id).first()
    if billing:
        billing.balance += amount
        db.commit()
        db.refresh(billing)
        return billing
    return None

#Списание кредитов (Бизнес-логика)
def spend_credits(db: Session, user_id: str, amount: int):
    billing = db.query(BillingAccount).filter(BillingAccount.user_id == user_id).first()
    if billing and billing.balance >= amount:
        billing.balance -= amount
        db.commit()
        return True
    return False

#Создание задачи (запись в историю)
def create_task(db: Session, user_id: str, model_name: str, prompt: str):
    new_task = MLTask(
        user_id=user_id,
        model_name=model_name,
        prompt=prompt,
        status="COMPLETED", # Для теста сразу ставим завершено
        image_url=f"http://fake-storage.com/{user_id}/img.png"
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

#Получение истории транзакций (задач) пользователя
def get_user_history(db: Session, user_id: str):
    return db.query(MLTask).filter(MLTask.user_id == user_id).order_by(MLTask.created_at.desc()).all()