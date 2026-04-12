from database import SessionLocal
from services import add_credits, spend_credits, create_task, get_user_history
from models import User

def test_system():
    db = SessionLocal()
    try:
        # Нахождение админа, который создал init_db.py
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            print("Ошибка: Админ не найден. Сначала запусти init_db.py")
            return

        print(f"--- Тест для пользователя: {admin.username} ---")

        # Проверка начального баланса
        print(f"Баланс до: {admin.billing.balance}")

        # Пополнение баланса
        add_credits(db, admin.id, 50)
        print(f"Пополнение +50. Текущий баланс: {admin.billing.balance}")

        # Списывание кредитов за генерацию
        if spend_credits(db, admin.id, 20):
            print("Списание 20 кредитов: УСПЕШНО")
            # Запись задачи в историю
            create_task(db, admin.id, "Google Nano Banana", "Cyberpunk cat in a hat")
        
        print(f"Итоговый баланс после списания: {admin.billing.balance}")

        # Получение и вывод истории
        print("\n--- История задач из базы данных ---")
        history = get_user_history(db, admin.id)
        for task in history:
            print(f"[{task.created_at.strftime('%Y-%m-%d %H:%M')}] {task.model_name}: {task.prompt} (Статус: {task.status})")

    finally:
        db.close()

if __name__ == "__main__":
    test_system()