import json
import base64
import time
import logging
from .rsa import RSA
from .keygen import generate_rsa

logger = logging.getLogger(__name__)

# Инициализируем RSA с ключами
# Генерируем ключи один раз при импорте модуля
_rsa_instance = RSA()
_rsa_keys = generate_rsa(2048)  # Используем 2048 бит для ключей

# Преобразуем ключи из mpz в int для работы
public_key = (int(_rsa_keys["public_key"][0]), int(_rsa_keys["public_key"][1]))
private_key = (int(_rsa_keys["private_key"][0]), int(_rsa_keys["private_key"][1]))

_rsa_instance.set_keys(
    public_key=public_key,
    private_key=private_key
)


def rsa_encrypt(text: str) -> str:
    """
    Шифрует строку при помощи RSA.
    Использует класс RSA из core/utils/rsa/.
    Возвращает зашифрованные данные в формате base64 JSON.
    """
    start_time = time.time()
    logger.info(f"[RSA ENCRYPT] Начало шифрования. Длина текста: {len(text)} символов")
    
    # Шифруем текст (получаем список чисел)
    encrypt_start = time.time()
    encrypted_list = _rsa_instance.encrypt(text)
    encrypt_time = time.time() - encrypt_start
    logger.info(f"[RSA ENCRYPT] Шифрование завершено за {encrypt_time:.4f} сек. Зашифровано {len(encrypted_list)} символов")
    
    # Преобразуем все элементы списка в int (для сериализации mpz в JSON)
    convert_start = time.time()
    encrypted_list = [int(x) for x in encrypted_list]
    convert_time = time.time() - convert_start
    logger.info(f"[RSA ENCRYPT] Преобразование в int завершено за {convert_time:.4f} сек")
    
    # Преобразуем список в JSON строку, затем в base64 для хранения
    json_start = time.time()
    json_str = json.dumps(encrypted_list)
    json_time = time.time() - json_start
    logger.info(f"[RSA ENCRYPT] JSON сериализация завершена за {json_time:.4f} сек. Размер JSON: {len(json_str)} символов")
    
    # Логируем результаты перед base64 кодированием
    logger.info("=" * 80)
    logger.info("[RSA ENCRYPT] РЕЗУЛЬТАТЫ ПЕРЕД BASE64 КОДИРОВАНИЕМ:")
    logger.info(f"[RSA ENCRYPT] Зашифрованный список (первые 5 элементов): {encrypted_list[:5]}")
    logger.info(f"[RSA ENCRYPT] Всего зашифрованных элементов: {len(encrypted_list)}")
    logger.info(f"[RSA ENCRYPT] JSON строка (первые 200 символов): {json_str[:200]}...")
    logger.info(f"[RSA ENCRYPT] Размер JSON строки: {len(json_str)} байт")
    logger.info("[RSA ENCRYPT] ИНФОРМАЦИЯ О ГОСТ:")
    logger.info("[RSA ENCRYPT] ГОСТ Р 34.10-2012 определяет использование RSA для цифровой подписи")
    logger.info("[RSA ENCRYPT] ГОСТ Р 34.10-2018 (актуальная версия) также поддерживает RSA")
    logger.info("[RSA ENCRYPT] По ГОСТу, зашифрованные данные должны представлять собой последовательность")
    logger.info("[RSA ENCRYPT] больших целых чисел (каждое число - результат шифрования одного символа)")
    logger.info("[RSA ENCRYPT] Формат вывода: список целых чисел в JSON, затем кодируется в base64")
    logger.info("[RSA ENCRYPT] Каждое число в списке - это результат операции: c = m^e mod n")
    logger.info("[RSA ENCRYPT] где m - код символа (ord), e - публичная экспонента, n - модуль")
    logger.info("=" * 80)
    
    base64_start = time.time()
    result = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
    base64_time = time.time() - base64_start
    total_time = time.time() - start_time
    logger.info(f"[RSA ENCRYPT] Base64 кодирование завершено за {base64_time:.4f} сек")
    logger.info(f"[RSA ENCRYPT] Полное время шифрования: {total_time:.4f} сек (шифрование: {encrypt_time:.4f}, конвертация: {convert_time:.4f}, JSON: {json_time:.4f}, Base64: {base64_time:.4f})")
    
    return result


def rsa_decrypt(cipher_b64: str) -> str:
    """
    Расшифровывает строку, зашифрованную через rsa_encrypt.
    """
    start_time = time.time()
    logger.info(f"[RSA DECRYPT] Начало расшифрования. Длина base64 строки: {len(cipher_b64)} символов")
    
    # Декодируем base64 в JSON строку
    base64_start = time.time()
    json_str = base64.b64decode(cipher_b64).decode("utf-8")
    base64_time = time.time() - base64_start
    logger.info(f"[RSA DECRYPT] Base64 декодирование завершено за {base64_time:.4f} сек. Размер JSON: {len(json_str)} символов")
    
    # Преобразуем JSON строку в список чисел
    json_start = time.time()
    encrypted_list = json.loads(json_str)
    json_time = time.time() - json_start
    logger.info(f"[RSA DECRYPT] JSON десериализация завершена за {json_time:.4f} сек. Загружено {len(encrypted_list)} зашифрованных символов")
    
    # Расшифровываем список чисел в строку
    decrypt_start = time.time()
    result = _rsa_instance.decrypt(encrypted_list)
    decrypt_time = time.time() - decrypt_start
    total_time = time.time() - start_time
    logger.info(f"[RSA DECRYPT] Расшифрование завершено за {decrypt_time:.4f} сек. Расшифровано {len(result)} символов")
    logger.info(f"[RSA DECRYPT] Полное время расшифрования: {total_time:.4f} сек (Base64: {base64_time:.4f}, JSON: {json_time:.4f}, расшифрование: {decrypt_time:.4f})")
    
    return result


# Экспортируем также класс RSA для прямого использования
__all__ = ['RSA', 'rsa_encrypt', 'rsa_decrypt', 'generate_rsa']
