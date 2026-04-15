from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from api.deps import get_current_user
from models.user import User
import schemas, services.ml_service

router = APIRouter(prefix="/predict", tags=["Predictions"])

@router.post("/", response_model=schemas.TaskRead)
def predict(prompt: str, model_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = services.ml_service.create_prediction_task(db, current_user.id, model_name, prompt)
    if not task:
        raise HTTPException(status_code=402, detail="Insufficient funds")
    return task