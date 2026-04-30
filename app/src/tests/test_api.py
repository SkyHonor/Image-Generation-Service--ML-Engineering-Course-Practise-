import pytest
from fastapi.testclient import TestClient
import uuid

# Импортируем наше приложение
from main import app

# Создаем виртуального "клиента" (имитация браузера/пользователя)
client = TestClient(app)

# Генерируем уникальные данные для каждого запуска тестов
test_email = f"testuser_{uuid.uuid4().hex[:6]}@example.com"
test_password = "strong_password123"
test_token = ""
user_id = ""

def test_1_register_user():
    """Сценарий 1.1: Успешная регистрация"""
    response = client.post("/auth/register", json={
        "username": "Test QA",
        "email": test_email,
        "password": test_password
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["email"] == test_email
    
    global user_id
    user_id = data["id"]

def test_2_register_duplicate_user():
    """Сценарий 1.4: Обработка ошибок при неверных данных (дубликат)"""
    response = client.post("/auth/register", json={
        "username": "Clone",
        "email": test_email, # Тот же email
        "password": "123"
    })
    # Должна вернуться ошибка 400
    assert response.status_code == 400

def test_3_login_user():
    """Сценарий 1.2: Успешная авторизация"""
    response = client.post("/auth/login", data={
        "username": test_email,
        "password": test_password
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    
    global test_token
    test_token = data["access_token"]

def test_4_get_balance():
    """Сценарий 2.1: Получение начального баланса"""
    response = client.get("/balance/", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == 200
    assert response.json()["balance"] == 10 # При регистрации дается 10 кредитов

def test_5_predict_success():
    """Сценарий 4.1 и 3.1: Успешная отправка на предсказание и списание"""
    # Тратим стартовые 10 кредитов
    response = client.post("/predict/", 
        json={"model_name": "Test Model", "prompt": "Test prompt"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["status"] == "processing"

    # Проверяем, что баланс стал 0
    balance_response = client.get("/balance/", headers={"Authorization": f"Bearer {test_token}"})
    assert balance_response.json()["balance"] == 0

def test_6_predict_insufficient_funds():
    """Сценарий 3.2: Запрет списания при недостаточном балансе"""
    # Пытаемся заказать еще раз при нулевом балансе
    response = client.post("/predict/", 
        json={"model_name": "Test Model", "prompt": "I have no money"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    # Должна вернуться ошибка 402 (Payment Required)
    assert response.status_code == 402

def test_7_predict_invalid_data():
    """Сценарий 4.3: Обработка некорректных входных данных"""
    response = client.post("/predict/", 
        json={"model_name": "Test Model"}, # Забыли поле prompt
        headers={"Authorization": f"Bearer {test_token}"}
    )
    # Pydantic должен вернуть ошибку валидации 422
    assert response.status_code == 422

def test_8_deposit_funds():
    """Сценарий 2.2 и 2.3: Пополнение баланса и корректное обновление"""
    response = client.post("/balance/deposit?amount=50", 
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert response.json()["balance"] == 50

def test_9_check_history():
    """Сценарий 5: Проверка истории транзакций и задач"""
    # Проверяем задачи
    tasks_response = client.get("/history/tasks", headers={"Authorization": f"Bearer {test_token}"})
    assert tasks_response.status_code == 200
    assert len(tasks_response.json()) == 1 # Был один успешный запрос в test_5

    # Проверяем транзакции (Создание кошелька(10), Списание(-10), Пополнение(+50))
    tx_response = client.get("/history/transactions", headers={"Authorization": f"Bearer {test_token}"})
    assert tx_response.status_code == 200
    tx_data = tx_response.json()
    assert len(tx_data) == 3