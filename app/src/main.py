from fastapi import FastAPI
from api import auth, billing, predictions
from database.session import engine
from models.base import Base

# Создаем таблицы при запуске
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ML Image Generation Service")

# Подключаем роутеры (наши разделенные файлы)
app.include_router(auth.router)
app.include_router(billing.router)
app.include_router(predictions.router)