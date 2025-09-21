import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from core.config import settings

def create_jwt_token(user_id: int) -> str:
    """
    Создать JWT токен по id пользователя.
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(user_id), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.SECRET_ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str) -> Optional[int]:
    """
    Проверить и расшифровать токен.
    Возвращает user_id или None если токен невалидный/просроченный.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.SECRET_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
