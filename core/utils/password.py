import os
import binascii
import hmac
from core.utils.stribog import Stribog
import logging

logger = logging.getLogger(__name__)

def _streebog512(data: bytes) -> bytes:
    """Вычисляет хэш Стрибог 512 бит согласно ГОСТ Р 34.11-2012."""
    return Stribog(data, digest_size=512).digest()


def get_password_hash(password: str) -> str:
    """Возвращает строку-хэш пароля в формате streebog512$salt$hash."""
    salt = os.urandom(16)
    pwd_bytes = password.encode("utf-8")
    digest = _streebog512(salt + pwd_bytes)
    return f"streebog512${binascii.hexlify(salt).decode()}${binascii.hexlify(digest).decode()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет совпадение пароля с хранимым хэшем."""
    try:
        parts = hashed_password.split("$")
        alg, salt_hex, digest_hex = parts
        if alg.lower() != "streebog512":
            return False
        salt = binascii.unhexlify(salt_hex)
        expected_digest = binascii.unhexlify(digest_hex)
        pwd_bytes = plain_password.encode("utf-8")
        computed = _streebog512(salt + pwd_bytes)

    except Exception:
        return False

    return hmac.compare_digest(computed, expected_digest)


# import bcrypt
# import logging

# logger = logging.getLogger(__name__)

# def get_password_hash(password: str) -> str:
#     """
#     Хеширование пароля с использованием bcrypt.
    
#     Args:
#         password: Пароль для хеширования
        
#     Returns:
#         str: Хешированный пароль
#     """
#     salt = bcrypt.gensalt()
#     return bcrypt.hashpw(password.encode(), salt).decode()

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """
#     Проверка соответствия пароля его хешу.
    
#     Args:
#         plain_password: Обычный пароль для проверки
#         hashed_password: Хешированный пароль для сравнения
        
#     Returns:
#         bool: True если пароли совпадают, False в противном случае
#     """
#     result = bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
#     return result 