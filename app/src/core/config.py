import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "ML Image Generation Service"
    
    PREDICTION_COST: int = 10
    
    # Генерация случайного секретного ключа для подписи токенов
    SECRET_KEY: str = os.getenv("SECRET_KEY", "7d92f587a8b38d389c8a8d1e3d3b3c3")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()