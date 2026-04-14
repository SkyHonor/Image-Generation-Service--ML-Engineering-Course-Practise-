from sqlalchemy.orm import Session
from models import User, BillingAccount, MLTask, MLModel, Transaction, TransactionType, TaskStatus
from security import get_password_hash

# Создание пользователя (с хешированием пароля)
def create_user(db: Session, username: str, email: str, password: str):
    hashed_password = get_password_hash(password)
    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.add(new_user)
    db.flush()
    
    new_billing = BillingAccount(user_id=new_user.id, balance=10)
    db.add(new_billing)
    db.commit()
    return new_user

# Пополнение баланса (с записью в историю транзакций)
def add_credits(db: Session, user_id: str, amount: int):
    billing = db.query(BillingAccount).filter(BillingAccount.user_id == user_id).first()
    if billing:
        billing.balance += amount
        
        # Создаем запись о транзакции
        new_tx = Transaction(
            user_id=user_id, 
            amount=amount, 
            transaction_type=TransactionType.DEPOSIT
        )
        db.add(new_tx)
        db.commit()
        return True
    return False

# Списание кредитов (с записью в историю транзакций)
def spend_credits(db: Session, user_id: str, amount: int):
    billing = db.query(BillingAccount).filter(BillingAccount.user_id == user_id).first()
    if billing and billing.balance >= amount:
        billing.balance -= amount
        
        # Создаем запись о списании
        new_tx = Transaction(
            user_id=user_id, 
            amount=-amount,
            transaction_type=TransactionType.WITHDRAWAL
        )
        db.add(new_tx)
        db.commit()
        return True
    return False

# Создание задачи (с использованием Enum статуса)
def create_task(db: Session, user_id: str, model_name: str, prompt: str):
    new_task = MLTask(
        user_id=user_id,
        model_name=model_name,
        prompt=prompt,
        status=TaskStatus.COMPLETED, # Используем Enum
        image_url=f"http://fake-storage.com/{user_id}/img.png"
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# Получение истории задач пользователя (с сортировкой)
def get_user_history(db: Session, user_id: str):
    return db.query(MLTask).filter(MLTask.user_id == user_id).order_by(MLTask.created_at.desc()).all()

# Получение истории ТРАНЗАКЦИЙ пользователя (для полноты системы)
def get_transaction_history(db: Session, user_id: str):
    return db.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.created_at.desc()).all()