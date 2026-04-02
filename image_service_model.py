from typing import List, Dict, Optional
from datetime import datetime
import uuid
from abc import ABC, abstractmethod

class User:
    """Сущность пользователя сервиса."""
    def __init__(self, username: str, email: str):
        self.username: str = username
        self.email: str = email
        self.__user_id: str = str(uuid.uuid4())

    def get_user_id(self) -> str:
        return self.__user_id


class BillingAccount:
    """Сущность для управления балансом (Биллинг)."""
    def __init__(self, user: User, initial_credits: int = 10):
        self.account_id: str = str(uuid.uuid4())
        self.owner_id: str = user.get_user_id()
        self.__balance: int = initial_credits

    def get_balance(self) -> int:
        return self.__balance

    def deduct_credits(self, amount: int = 1) -> bool:
        if self.__balance >= amount:
            self.__balance -= amount
            return True
        print(f"Ошибка биллинга: Недостаточно средств на счете {self.account_id}")
        return False


class GeneratedImage:
    """Результат генерации."""
    def __init__(self, image_url: str, resolution: str):
        self.image_id: str = str(uuid.uuid4())
        self.image_url: str = image_url
        self.resolution: str = resolution
        self.created_at: str = datetime.now().isoformat()


class BaseImageGenerator(ABC):
    """Базовый абстрактный класс для ML-моделей."""
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
    """Интеграция с моделью Google Gemini."""
    def __init__(self, api_key: str):
        super().__init__(model_name="Google Gemini Imagen", api_key=api_key)

    def generate(self, prompt: str, resolution: str = "1024x1024") -> Optional[GeneratedImage]:
        if not self._is_connected:
            self.connect()
        
        # Имитация работы API
        fake_image_url = f"https://storage.googleapis.com/fake-bucket/{uuid.uuid4()}.png"
        return GeneratedImage(image_url=fake_image_url, resolution=resolution)


class MLTask:
    """Сущность задачи для ML-модели (Жизненный цикл запроса)."""
    def __init__(self, user: User, prompt: str, model: BaseImageGenerator):
        self.task_id: str = str(uuid.uuid4())
        self.user_id: str = user.get_user_id()
        self.prompt: str = prompt
        self.model: BaseImageGenerator = model
        
        self.status: str = "CREATED"  # Возможные статусы: CREATED, PROCESSING, COMPLETED, FAILED
        self.result: Optional[GeneratedImage] = None
        self.created_at: str = datetime.now().isoformat()

    def execute(self) -> None:
        """Метод запуска задачи на исполнение."""
        self.status = "PROCESSING"
        print(f"Задача {self.task_id}: Статус изменен на {self.status}")
        
        try:
            # Вызов полиморфного метода ML модели
            generated_result = self.model.generate(prompt=self.prompt, resolution="1024x1024")
            
            if generated_result:
                self.result = generated_result
                self.status = "COMPLETED"
            else:
                self.status = "FAILED"
        except Exception as e:
            print(f"Ошибка при выполнении задачи: {e}")
            self.status = "FAILED"
            
        print(f"Задача {self.task_id}: Завершена со статусом {self.status}")


class TaskHistory:
    """Сервис хранения истории выполненных задач."""
    def __init__(self):
        self.__logs: List[Dict[str, str]] =[]

    def log_task(self, task: MLTask) -> None:
        record = {
            "task_id": task.task_id,
            "user_id": task.user_id,
            "model_used": task.model.model_name,
            "prompt": task.prompt,
            "status": task.status,
            "image_url": task.result.image_url if task.result else "None",
            "timestamp": task.created_at
        }
        self.__logs.append(record)

    def get_logs_for_user(self, user: User) -> List[Dict[str, str]]:
        return[log for log in self.__logs if log["user_id"] == user.get_user_id()]