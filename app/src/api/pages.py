from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.session import get_db
from api.deps import get_current_user
from models.user import User

router = APIRouter(tags=["Pages"])

# Указываем, где лежат наши HTML-файлы
templates = Jinja2Templates(directory="frontend")

@router.get("/")
def render_index(request: Request):
    """Отдает страницу входа"""
    return templates.TemplateResponse(
        request=request, 
        name="index.html"
    )

@router.get("/dashboard")
def render_dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Отдает личный кабинет, сразу заполненный данными из БД (Jinja2 контекст)"""
    
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": current_user,
            "balance": current_user.billing.balance if current_user.billing else 0,
            "tasks": current_user.tasks,
            "transactions": current_user.transactions
        }
    )