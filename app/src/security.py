import hashlib

def get_password_hash(password: str) -> str:
    #Превращает пароль в хеш
    return hashlib.sha256(password.encode()).hexdigest()