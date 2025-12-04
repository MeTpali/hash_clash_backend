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
    
    # Логируем результаты перед hex кодированием
    logger.info("=" * 80)
    logger.info("[STRIBOG] РЕЗУЛЬТАТЫ ПЕРЕД HEX КОДИРОВАНИЕМ:")
    logger.info(f"[STRIBOG] Соль (salt) в байтах: {salt.hex()}")
    logger.info(f"[STRIBOG] Размер соли: {len(salt)} байт (128 бит)")
    logger.info(f"[STRIBOG] Хэш (digest) в байтах: {digest.hex()}")
    logger.info(f"[STRIBOG] Размер хэша: {len(digest)} байт (512 бит)")
    logger.info(f"[STRIBOG] Первые 32 байта хэша (hex): {digest[:32].hex()}")
    logger.info("[STRIBOG] ИНФОРМАЦИЯ О ГОСТ:")
    logger.info("[STRIBOG] ГОСТ Р 34.11-2012 (Стрибог) - функция хеширования")
    logger.info("[STRIBOG] Размер блока: 512 бит (64 байта)")
    logger.info("[STRIBOG] Размер хэша: 512 бит (64 байта) или 256 бит (32 байта)")
    logger.info("[STRIBOG] Алгоритм использует:")
    logger.info("[STRIBOG]   - Преобразование PS (перестановка и замена байтов)")
    logger.info("[STRIBOG]   - Преобразование L (линейное преобразование)")
    logger.info("[STRIBOG]   - Функцию сжатия g, которая использует блочный шифр E")
    logger.info("[STRIBOG] По ГОСТу, результат хеширования представляет собой:")
    logger.info("[STRIBOG]   - 512-битное значение (64 байта) для Stribog-512")
    logger.info("[STRIBOG]   - 256-битное значение (32 байта) для Stribog-256")
    logger.info("[STRIBOG] Формат вывода: hex-строка (двоичные данные в шестнадцатеричном представлении)")
    logger.info("[STRIBOG] Каждый байт представляется двумя шестнадцатеричными символами")
    logger.info("=" * 80)
    
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
        
        # Логируем результаты перед сравнением
        logger.info("=" * 80)
        logger.info("[STRIBOG VERIFY] РЕЗУЛЬТАТЫ ПЕРЕД СРАВНЕНИЕМ:")
        logger.info(f"[STRIBOG VERIFY] Вычисленный хэш (hex): {computed.hex()}")
        logger.info(f"[STRIBOG VERIFY] Ожидаемый хэш (hex): {expected_digest.hex()}")
        logger.info(f"[STRIBOG VERIFY] Размер вычисленного хэша: {len(computed)} байт")
        logger.info(f"[STRIBOG VERIFY] Размер ожидаемого хэша: {len(expected_digest)} байт")
        logger.info("=" * 80)

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