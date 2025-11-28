import json
import base64
from .rsa import RSA
from .keygen import generate_rsa

# Инициализируем RSA с ключами
# Генерируем ключи один раз при импорте модуля
_rsa_instance = RSA()
_rsa_keys = generate_rsa(2048)  # Используем 2048 бит для ключей
_rsa_instance.set_keys(
    public_key=_rsa_keys["public_key"],
    private_key=_rsa_keys["private_key"]
)


def rsa_encrypt(text: str) -> str:
    """
    Шифрует строку при помощи RSA.
    Использует класс RSA из core/utils/rsa/.
    Возвращает зашифрованные данные в формате base64 JSON.
    """
    # Шифруем текст (получаем список чисел)
    encrypted_list = _rsa_instance.encrypt(text)
    
    # Преобразуем список в JSON строку, затем в base64 для хранения
    json_str = json.dumps(encrypted_list)
    return base64.b64encode(json_str.encode("utf-8")).decode("utf-8")


def rsa_decrypt(cipher_b64: str) -> str:
    """
    Расшифровывает строку, зашифрованную через rsa_encrypt.
    """
    # Декодируем base64 в JSON строку
    json_str = base64.b64decode(cipher_b64).decode("utf-8")
    
    # Преобразуем JSON строку в список чисел
    encrypted_list = json.loads(json_str)
    
    # Расшифровываем список чисел в строку
    return _rsa_instance.decrypt(encrypted_list)


# Экспортируем также класс RSA для прямого использования
__all__ = ['RSA', 'rsa_encrypt', 'rsa_decrypt', 'generate_rsa']
