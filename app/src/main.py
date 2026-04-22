from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api import auth, billing, predictions
from database.session import engine
from models.base import Base
from api import auth, billing, predictions, history

# Создаем таблицы при запуске
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ML Image Generation Service")

# Подключаем роутеры (наши разделенные файлы)
app.include_router(auth.router)
app.include_router(billing.router)
app.include_router(predictions.router)
app.include_router(history.router)

app.mount("/src/generated_images", StaticFiles(directory="generated_images"), name="images")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")