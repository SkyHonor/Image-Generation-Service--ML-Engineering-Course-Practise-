from sqlalchemy.orm import Session
from models.billing import BillingAccount, Transaction, TransactionType
from core.config import settings

def get_user_balance(db: Session, user_id: str):
    billing = db.query(BillingAccount).filter(BillingAccount.user_id == user_id).first()
    return billing.balance if billing else 0

def add_credits(db: Session, user_id: str, amount: int):
    billing = db.query(BillingAccount).filter(BillingAccount.user_id == user_id).first()
    if billing:
        billing.balance += amount
        db.add(Transaction(user_id=user_id, amount=amount, transaction_type=TransactionType.DEPOSIT))
        db.commit()
        return billing
    return None

def spend_credits_for_predict(db: Session, user_id: str):
    billing = db.query(BillingAccount).filter(BillingAccount.user_id == user_id).first()
    cost = settings.PREDICTION_COST # ИСПОЛЬЗУЕМ КОНСТАНТУ ИЗ ГЛОБАЛЬНЫХ НАСТРОЕК
    if billing and billing.balance >= cost:
        billing.balance -= cost
        db.add(Transaction(user_id=user_id, amount=-cost, transaction_type=TransactionType.WITHDRAWAL))
        db.commit()
        return True
    return False