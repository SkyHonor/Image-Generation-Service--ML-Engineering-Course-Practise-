from typing import List, Dict, Optional
from datetime import datetime
import uuid
from abc import ABC, abstractmethod

class GeneratedImage:
    """Сущность сгенерированного изображения."""
    def __init__(self, image_url: str, prompt: str, resolution: str):
        self.image_id: str = str(uuid.uuid4())
        self.image_url: str = image_url
        self.prompt: str = prompt
        self.resolution: str = resolution
        self.created_at: str = datetime.now().isoformat()

class User:
    """Сущность пользователя сервиса."""
    def __init__(self, username: str, email: str, initial_credits: int = 10):
        self.username: str = username
        self.email: str = email
        self.__user_id: str = str(uuid.uuid4())
        self.__balance: int = initial_credits

    def get_user_id(self) -> str:
        return self.__user_id

    def get_balance(self) -> int:
        return self.__balance

    def deduct_credits(self, amount: int = 1) -> bool:
        if self.__balance >= amount:
            self.__balance -= amount
            return True
        print(f"Ошибка: Недостаточно баланса у пользователя {self.username}")
        return False

class BaseImageGenerator(ABC):
    """Базовый абстрактный класс для ML-моделей генерации."""
    def __init__(self, model_name: str, api_key: str):
        self.model_name: str = model_name
        self.__api_key: str = api_key 
        self._is_connected: bool = False

    def connect(self) -> None:
        print(f"Подключение к провайдеру {self.model_name}...")
        self._is_connected = True

    @abstractmethod
    def generate(self, prompt: str, resolution: str) -> Optional[GeneratedImage]:
        pass

class GeminiImageGenerator(BaseImageGenerator):
    """Интеграция с конкретной моделью Google Gemini Image."""
    def __init__(self, api_key: str):
        super().__init__(model_name="Google Gemini Imagen", api_key=api_key)

    def generate(self, prompt: str, resolution: str = "1024x1024") -> Optional[GeneratedImage]:
        if not self._is_connected:
            self.connect()
        
        print(f"[{self.model_name}] Отправка API запроса в Google: '{prompt}'")
        
        # Имитация ответа от API (планируется в будущих уроках интеграция Google Nano Banana)
        fake_image_url = f"https://storage.googleapis.com/fake-bucket/{uuid.uuid4()}.png"
        return GeneratedImage(image_url=fake_image_url, prompt=prompt, resolution=resolution)

class TaskHistory:
    """Сервис хранения истории генераций."""
    def __init__(self):
        self.__logs: List[Dict[str, str]] =[]

    def log_generation(self, user: User, model: BaseImageGenerator, image: GeneratedImage) -> None:
        record = {
            "user_id": user.get_user_id(),
            "model_used": model.model_name,
            "prompt": image.prompt,
            "image_url": image.image_url,
            "timestamp": image.created_at
        }
        self.__logs.append(record)
        print("Транзакция успешно сохранена.")

    def get_logs_for_user(self, user: User) -> List[Dict[str, str]]:
        return [log for log in self.__logs if log["user_id"] == user.get_user_id()]