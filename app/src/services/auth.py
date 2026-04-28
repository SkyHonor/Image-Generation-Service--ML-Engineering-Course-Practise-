from sqlalchemy.orm import Session
from models.user import User
from models.billing import BillingAccount, Transaction, TransactionType
from core.security import get_password_hash, verify_password
import schemas

def create_user(db: Session, user_data: schemas.UserCreate):
    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(username=user_data.username, email=user_data.email, password_hash=hashed_pwd)
    db.add(new_user)
    db.flush()
    
    # Создаем кошелек (стартовые 10 кредитов)
    new_billing = BillingAccount(user_id=new_user.id, balance=10)
    db.add(new_billing)
    
    # Фиксируем стартовый бонус в истории транзакций
    bonus_tx = Transaction(
        user_id=new_user.id, 
        amount=10, 
        transaction_type=TransactionType.DEPOSIT
    )
    db.add(bonus_tx)
    
    db.commit()
    return new_user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user