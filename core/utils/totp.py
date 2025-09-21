import pyotp
import base64
import os
import logging

logger = logging.getLogger(__name__)


def generate_totp_secret() -> str:
    """
    Генерация случайного секрета для TOTP.
    Возвращает строку в base32 (совместима с Google Authenticator).
    """
    secret = base64.b32encode(os.urandom(20)).decode("utf-8")
    logger.info("Generated new TOTP secret")
    return secret


def get_totp_uri(secret: str, username: str, issuer: str = "HashClash") -> str:
    """
    Создание otpauth:// URI для подключения к Google Authenticator.
    
    Args:
        secret: base32-секрет
        username: логин/почта пользователя
        issuer: название приложения
    
    Returns:
        str: otpauth URI
    """
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=username, issuer_name=issuer)
    logger.info(f"Generated TOTP URI for user: {username}")
    return uri


def verify_totp(secret: str, code: str) -> bool:
    """
    Проверка TOTP-кода.
    
    Args:
        secret: base32-секрет
        code: введённый пользователем код
    
    Returns:
        bool: True, если код корректен, иначе False
    """
    try:
        totp = pyotp.TOTP(secret)
        is_valid = totp.verify(code)
        
        if is_valid:
            logger.info("TOTP code verification successful")
        else:
            logger.warning(f"TOTP code verification failed: {code}")
            
        return is_valid
        
    except Exception as e:
        logger.error(f"Error verifying TOTP code: {e}")
        return False
