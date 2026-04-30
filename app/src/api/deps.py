from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from core.config import settings
from database.session import get_db
from models.user import User

# auto_error=False позволяет нам проверять и другие места (например, куки)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

def get_token(request: Request, token_from_header: str = Depends(oauth2_scheme)):
    # Сначала ищем токен в Куках (для Web-интерфейса Jinja2)
    token = request.cookies.get("access_token")
    
    # Если в куках нет, ищем в Заголовке (для Swagger UI)
    if not token:
        token = token_from_header
        
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return token

def get_current_user(db: Session = Depends(get_db), token: str = Depends(get_token)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user