# 🍌 Nano Banana ML - Image Generation Service

Полноценный асинхронный микросервис для генерации изображений с помощью нейросетей (Google Gemini 3.1 Flash), построенный на микросервисной архитектуре с использованием брокера сообщений.

## 🛠 Технологический стек
*   **Backend API**: FastAPI, Pydantic, Python 3.10+
*   **База данных**: PostgreSQL, SQLAlchemy (ORM)
*   **Асинхронные очереди**: RabbitMQ, Pika
*   **Frontend**: HTML5, Bootstrap 5, Vanilla JS, Server-Side Rendering (Jinja2)
*   **Инфраструктура**: Docker, Docker Compose
*   **Тестирование**: Pytest, FastAPI TestClient
*   **ML Интеграция**: Google Nano Banana

## 🚀 Архитектура системы
1.  **FastAPI (Publisher)** принимает запросы от пользователей (через Web UI или Swagger), списывает кредиты с баланса и публикует задачу в RabbitMQ.
2.  **RabbitMQ (Broker)** гарантирует сохранность сообщений и балансирует нагрузку между воркерами (Round-robin).
3.  **Workers (Consumers)** изолированно работают в Docker-контейнерах, получают задачи, делают запросы к Google Gemini API, сохраняют сгенерированные изображения и обновляют статусы в БД.
