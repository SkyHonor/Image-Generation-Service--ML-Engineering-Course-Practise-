from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import services
from database import get_db, init_db

app = FastAPI(title="ML Image Generation Service")

# Инициализируем БД при старте
@app.on_event("startup")
def on_startup():
    init_db()

# --- 1. Регистрация ---
@app.post("/auth/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return services.create_user(db, user_data.username, user_data.email, user_data.password)

# --- 2. Работа с балансом ---
@app.get("/balance/{user_id}", response_model=schemas.BalanceRead)
def get_balance(user_id: str, db: Session = Depends(get_db)):
    billing = db.query(models.BillingAccount).filter(models.BillingAccount.user_id == user_id).first()
    if not billing:
        raise HTTPException(status_code=404, detail="User not found")
    return {"balance": billing.balance}

@app.post("/balance/deposit", response_model=schemas.BalanceRead)
def deposit(data: schemas.DepositRequest, db: Session = Depends(get_db)):
    success = services.add_credits(db, data.user_id, data.amount)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    billing = db.query(models.BillingAccount).filter(models.BillingAccount.user_id == data.user_id).first()
    return {"balance": billing.balance}

# --- 3. ML Предсказания ---
@app.post("/predict", response_model=schemas.TaskRead)
def predict(request: schemas.PredictionRequest, db: Session = Depends(get_db)):
    # 1. Проверяем баланс (цена генерации = 10)
    cost = 10
    if not services.spend_credits(db, request.user_id, cost):
        raise HTTPException(status_code=402, detail="Insufficient funds")
    
    # 2. Создаем задачу
    task = services.create_task(db, request.user_id, request.model_name, request.prompt)
    return task

# --- 4. История ---
@app.get("/history/tasks/{user_id}", response_model=List[schemas.TaskRead])
def list_tasks(user_id: str, db: Session = Depends(get_db)):
    return services.get_user_history(db, user_id)

@app.get("/history/transactions/{user_id}", response_model=List[schemas.TransactionRead])
def list_transactions(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.transactions