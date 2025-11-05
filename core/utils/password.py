import os
import binascii
import hmac
from pygost.gost34112012 import GOST34112012
import logging

ITERATIONS = 1000  # можно поднять до 100_000+ для продакшена

logger = logging.getLogger(__name__)

def _streebog512(data: bytes) -> bytes:
    """Вычисляет хэш Стрибог 512 бит."""
    return GOST34112012(data=data).digest()


def _derive(password: str, salt: bytes, iterations: int) -> bytes:
    """Генерация итеративного хэша пароля."""
    logger.info(f"Deriving password hash for password: {password}")
    pwd_bytes = password.encode("utf-8")
    digest = _streebog512(salt + pwd_bytes)
    for _ in range(iterations - 1):
        digest = _streebog512(digest)
    return digest


def get_password_hash(password: str) -> str:
    """Возвращает строку-хэш пароля в формате streebog512$ITERATIONS$salt$hash."""
    salt = os.urandom(16)
    digest = _derive(password, salt, ITERATIONS)
    return f"streebog512${ITERATIONS}${binascii.hexlify(salt).decode()}${binascii.hexlify(digest).decode()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет совпадение пароля с хранимым хэшем."""
    try:
        alg, iter_str, salt_hex, digest_hex = hashed_password.split("$")
        if alg.lower() != "streebog512":
            return False
        iterations = int(iter_str)
        salt = binascii.unhexlify(salt_hex)
        expected_digest = binascii.unhexlify(digest_hex)
    except Exception:
        return False

    computed = _derive(plain_password, salt, iterations)
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