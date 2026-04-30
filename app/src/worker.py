import pika
import json
import os
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types

from database.session import SessionLocal
from models.prediction import MLTask, TaskStatus
from services.billing import refund_credits
from core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Папка для сохранения готовых картинок
OUTPUT_DIR = "src/generated_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def callback(ch, method, properties, body):
    db = SessionLocal()
    task = None
    try:
        data = json.loads(body)
        task_id = data.get('task_id')
        raw_prompt = data.get('features', {}).get('prompt')

        if not task_id or not raw_prompt:
            print(" [x] Ошибка: Неверный формат сообщения")
            ch.basic_ack(delivery_tag=method.delivery_tag)            
            return

        print(f" [worker] Взял задачу: {task_id}. Промпт: '{raw_prompt}'")

        # Ищем задачу в БД
        task = db.query(MLTask).filter(MLTask.id == task_id).first()
        if not task:
            print(f" [x] Ошибка: Задача {task_id} не найдена в БД")
            return

        print(f" [worker] Отправляю запрос в Google Nano Banana 2 (gemini-3.1-flash-image-preview)...")
        
        # НАСТОЯЩАЯ ГЕНЕРАЦИЯ КАРТИНКИ
        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=raw_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"], # Жестко требуем именно картинку
            )
        )
        
        image_path = f"{OUTPUT_DIR}/{task_id}.png"
        
        # Вытаскиваем бинарные данные картинки из ответа и сохраняем через Pillow
        image_saved = False
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                img = Image.open(BytesIO(part.inline_data.data))
                img.save(image_path)
                image_saved = True
                break
                
        if not image_saved:
            raise Exception("Модель не вернула картинку (возможно, сработал фильтр безопасности NSFW)")
            
        print(f"[worker] Картинка успешно сгенерирована и сохранена в {image_path}!")

        # Обновляем статус в БД и прикрепляем ссылку на файл
        task.status = TaskStatus.COMPLETED
        task.image_url = f"/{image_path}"
        db.commit()

    except Exception as e:
        print(f" [x] ОШИБКА ML-МОДЕЛИ ИЛИ СИСТЕМЫ: {e}")
        # Возврат средств, если Гугл упал, нет интернета или промпт заблокирован
        if task:
            task.status = TaskStatus.FAILED
            db.commit()
            print(f" [worker] Делаю возврат {settings.PREDICTION_COST} кредитов пользователю {task.user_id}")
            refund_credits(db, task.user_id, settings.PREDICTION_COST)
            
    finally:
        db.close()
        # Обязательно подтверждаем RabbitMQ, что мы обработали сообщение (иначе очередь зависнет)
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    rabbit_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    
    # Увеличиваем таймауты пульса (heartbeat), так как генерация картинки может занимать 10-30 секунд
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbit_host,
            heartbeat=600,
            blocked_connection_timeout=600
        )
    )
    channel = connection.channel()

    # Берем имя очереди из конфига
    channel.queue_declare(queue=settings.RABBITMQ_QUEUE_NAME, durable=True)
    
    # Не давать воркеру больше одной задачи за раз (честная балансировка Round-robin)
    channel.basic_qos(prefetch_count=1)
    
    channel.basic_consume(queue=settings.RABBITMQ_QUEUE_NAME, on_message_callback=callback)

    print(" [*] Воркер запущен. Настоящая генерация через Nano Banana 2 активна!")
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()