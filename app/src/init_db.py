from database import engine, SessionLocal
from models import Base, User, BillingAccount, MLModel, Transaction, TransactionType
from security import get_password_hash

def run_init():
    #Создание таблицы в Postgres
    print("Создание таблиц...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        #Проверка, есть ли админ
        admin_email = "admin@example.com"
        exists = db.query(User).filter(User.email == admin_email).first()

        if not exists:
            print("Создаём данные...")
            #Создание пользователя
            admin = User(
                username="admin",
                email=admin_email,
                password_hash=get_password_hash("secret_admin_password")
            )
            db.add(admin)
            db.flush()

            #Создание кошелька админа
            admin_billing = BillingAccount(user_id=admin.id, balance=100)
            db.add(admin_billing)

            # Первая транзакция (начальный капитал)
            init_tx = Transaction(
                user_id=admin.id, 
                amount=100, 
                transaction_type=TransactionType.DEPOSIT
            )
            db.add(init_tx)

            #Создание базовых моделей
            gemini = MLModel(name="Google Nano Banana", api_key="gemini-key-123") #Здесь будет API ключ
            dalle = MLModel(name="DALL-E 3", api_key="dalle-key-456")
            db.add_all([gemini, dalle])

            db.commit()
            print ("База успешно инициализирована")
        else:
            print ("База уже содержит данные, пропуск инициализации")

    except Exception as e:
        print (f"Ошибка при инициализации: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_init()    