import pika
import json

def send_to_queue(task_data: dict):
    # Внутри Docker хост для подключения называется 'rabbitmq' (как в docker-compose)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Создаем очередь, если её нет. durable=True значит, что очередь выживет при перезагрузке RabbitMQ
    channel.queue_declare(queue='ml_tasks', durable=True)

    # Публикуем сообщение
    channel.basic_publish(
        exchange='',
        routing_key='ml_tasks',
        body=json.dumps(task_data),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Делает сообщение постоянным (сохранится на диск)
        )
    )
    connection.close()