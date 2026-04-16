import pika
import json
import time
import random
import os
from database.session import SessionLocal
from models import MLTask, TaskStatus

def callback(ch, method, properties, body):
    # 1. Распаковываем сообщение
    data = json.loads(body)
    task_id = data['task_id']
    print(f" [worker] Взял задачу: {task_id}")

    # 2. Имитируем "тяжелую" работу нейросети
    time.sleep(random.randint(5, 10)) 

    # 3. Обновляем статус в базе на COMPLETED
    db = SessionLocal()
    task = db.query(MLTask).filter(MLTask.id == task_id).first()
    if task:
        task.status = TaskStatus.COMPLETED
        task.image_url = f"https://my-storage.com/image_{task_id}.png"
        db.commit()
        print(f" [worker] Задача {task_id} выполнена!")
    db.close()

    # 4. Подтверждаем RabbitMQ, что задача удалена из очереди
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    # Подключаемся к брокеру
    rabbit_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
    channel = connection.channel()

    channel.queue_declare(queue='ml_tasks', durable=True)
    
    # Не давать воркеру больше одной задачи за раз (честная загрузка)
    channel.basic_qos(prefetch_count=1)
    
    channel.basic_consume(queue='ml_tasks', on_message_callback=callback)

    print(" [*] Воркер запущен и ждет задач. Нажми CTRL+C для выхода")
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()