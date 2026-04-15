from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from api.deps import get_current_user
from models.user import User
import schemas, services.billing

router = APIRouter(prefix="/balance", tags=["Billing"])

@router.get("/", response_model=schemas.BalanceRead)
# Вместо user_id теперь просим current_user
def get_balance(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    balance = services.billing.get_user_balance(db, current_user.id)
    return {"balance": balance}

@router.post("/deposit", response_model=schemas.BalanceRead)
def deposit(amount: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    services.billing.add_credits(db, current_user.id, amount)
    balance = services.billing.get_user_balance(db, current_user.id)
    return {"balance": balance}