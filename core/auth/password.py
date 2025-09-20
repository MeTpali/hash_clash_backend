import bcrypt
import logging

logger = logging.getLogger(__name__)

def get_password_hash(password: str) -> str:
    """
    Хеширование пароля с использованием bcrypt.
    
    Args:
        password: Пароль для хеширования
        
    Returns:
        str: Хешированный пароль
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверка соответствия пароля его хешу.
    
    Args:
        plain_password: Обычный пароль для проверки
        hashed_password: Хешированный пароль для сравнения
        
    Returns:
        bool: True если пароли совпадают, False в противном случае
    """
    result = bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    return result 