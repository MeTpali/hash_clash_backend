import json
import base64
import time
import logging
from .kuznechik import (
    kuznechik_encrypt, kuznechik_decrypt, DEFAULT_KEY,
    kuznechik_key_schedule, S, S_inv, L, L_inv
)

logger = logging.getLogger(__name__)

# Используем ключ по умолчанию для шифрования
_grasshopper_key = DEFAULT_KEY


def _kuznechik_encrypt_int(block_int: int, key: int) -> int:
    """
    Шифрует 128-битный блок (представленный как int) напрямую.
    """
    keys = kuznechik_key_schedule(key)
    x = block_int
    for round in range(9):
        x = L(S(x ^ keys[round]))
    return x ^ keys[-1]


def _kuznechik_decrypt_int(encrypted_int: int, key: int) -> int:
    """
    Расшифровывает 128-битный блок (представленный как int) напрямую.
    """
    keys = kuznechik_key_schedule(key)
    keys.reverse()
    x = encrypted_int
    for round in range(9):
        x = S_inv(L_inv(x ^ keys[round]))
    return x ^ keys[-1]


def grasshopper_encrypt(text: str) -> str:
    """
    Шифрует строку при помощи Kuznechik (Grasshopper).
    Разбивает текст на блоки по 16 байт (128 бит) и шифрует каждый блок.
    Возвращает зашифрованные данные в формате base64 JSON.
    """
    start_time = time.time()
    logger.info(f"[GRASSHOPPER ENCRYPT] Начало шифрования. Длина текста: {len(text)} символов")
    
    # Разбиваем текст на блоки по 16 байт (128 бит)
    encode_start = time.time()
    text_bytes = text.encode("utf-8")
    encode_time = time.time() - encode_start
    logger.info(f"[GRASSHOPPER ENCRYPT] Кодирование текста в UTF-8 завершено за {encode_time:.4f} сек. Размер: {len(text_bytes)} байт")
    
    block_size = 16
    num_blocks = (len(text_bytes) + block_size - 1) // block_size
    logger.info(f"[GRASSHOPPER ENCRYPT] Текст будет разбит на {num_blocks} блоков по {block_size} байт")
    
    encrypted_blocks = []
    
    # Обрабатываем текст блоками
    encrypt_start = time.time()
    for i in range(0, len(text_bytes), block_size):
        block_start = time.time()
        block_bytes = text_bytes[i:i + block_size]
        block_num = i // block_size + 1
        
        # Дополняем блок до 16 байт нулями, если необходимо
        if len(block_bytes) < block_size:
            block_bytes += b'\x00' * (block_size - len(block_bytes))
        
        # Преобразуем блок байтов в число (128 бит)
        block_int = int.from_bytes(block_bytes, byteorder='big')
        
        # Шифруем блок напрямую как число
        encrypted_block = _kuznechik_encrypt_int(block_int, _grasshopper_key)
        encrypted_blocks.append(str(encrypted_block))  # Преобразуем число в строку для JSON
        
        block_time = time.time() - block_start
        if block_num % 10 == 0 or block_time > 0.01:
            logger.info(f"[GRASSHOPPER ENCRYPT] Зашифрован блок {block_num}/{num_blocks} за {block_time:.4f} сек")
    
    encrypt_time = time.time() - encrypt_start
    logger.info(f"[GRASSHOPPER ENCRYPT] Шифрование {num_blocks} блоков завершено за {encrypt_time:.4f} сек (среднее: {encrypt_time/num_blocks:.6f} сек/блок)")
    
    # Преобразуем список зашифрованных блоков в JSON строку, затем в base64
    json_start = time.time()
    json_str = json.dumps(encrypted_blocks)
    json_time = time.time() - json_start
    logger.info(f"[GRASSHOPPER ENCRYPT] JSON сериализация завершена за {json_time:.4f} сек. Размер JSON: {len(json_str)} символов")
    
    # Логируем результаты перед base64 кодированием
    logger.info("=" * 80)
    logger.info("[GRASSHOPPER ENCRYPT] РЕЗУЛЬТАТЫ ПЕРЕД BASE64 КОДИРОВАНИЕМ:")
    logger.info(f"[GRASSHOPPER ENCRYPT] Зашифрованные блоки (первые 3 блока): {encrypted_blocks[:3]}")
    logger.info(f"[GRASSHOPPER ENCRYPT] Всего зашифрованных блоков: {len(encrypted_blocks)}")
    logger.info(f"[GRASSHOPPER ENCRYPT] Каждый блок представлен как большое целое число (128 бит)")
    logger.info(f"[GRASSHOPPER ENCRYPT] JSON строка (первые 200 символов): {json_str[:200]}...")
    logger.info(f"[GRASSHOPPER ENCRYPT] Размер JSON строки: {len(json_str)} байт")
    logger.info("[GRASSHOPPER ENCRYPT] ИНФОРМАЦИЯ О ГОСТ:")
    logger.info("[GRASSHOPPER ENCRYPT] ГОСТ Р 34.12-2015 (Кузнечик) - блочный шифр с размером блока 128 бит")
    logger.info("[GRASSHOPPER ENCRYPT] Размер ключа: 256 бит (используется два 128-битных ключа)")
    logger.info("[GRASSHOPPER ENCRYPT] Алгоритм состоит из 9 раундов с использованием:")
    logger.info("[GRASSHOPPER ENCRYPT]   - Нелинейного преобразования S (S-блоки)")
    logger.info("[GRASSHOPPER ENCRYPT]   - Линейного преобразования L (умножение в поле GF(2^8))")
    logger.info("[GRASSHOPPER ENCRYPT] По ГОСТу, зашифрованные данные представляют собой последовательность")
    logger.info("[GRASSHOPPER ENCRYPT] 128-битных блоков, каждый из которых зашифрован независимо")
    logger.info("[GRASSHOPPER ENCRYPT] Формат вывода: список больших целых чисел (по одному на блок) в JSON,")
    logger.info("[GRASSHOPPER ENCRYPT] затем кодируется в base64")
    logger.info("[GRASSHOPPER ENCRYPT] Каждое число в списке - это результат шифрования 16-байтового блока")
    logger.info("=" * 80)
    
    base64_start = time.time()
    result = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
    base64_time = time.time() - base64_start
    total_time = time.time() - start_time
    logger.info(f"[GRASSHOPPER ENCRYPT] Base64 кодирование завершено за {base64_time:.4f} сек")
    logger.info(f"[GRASSHOPPER ENCRYPT] Полное время шифрования: {total_time:.4f} сек (кодирование: {encode_time:.4f}, шифрование: {encrypt_time:.4f}, JSON: {json_time:.4f}, Base64: {base64_time:.4f})")
    
    return result


def grasshopper_decrypt(cipher_b64: str) -> str:
    """
    Расшифровывает строку, зашифрованную через grasshopper_encrypt.
    """
    start_time = time.time()
    logger.info(f"[GRASSHOPPER DECRYPT] Начало расшифрования. Длина base64 строки: {len(cipher_b64)} символов")
    
    # Декодируем base64 в JSON строку
    base64_start = time.time()
    json_str = base64.b64decode(cipher_b64).decode("utf-8")
    base64_time = time.time() - base64_start
    logger.info(f"[GRASSHOPPER DECRYPT] Base64 декодирование завершено за {base64_time:.4f} сек. Размер JSON: {len(json_str)} символов")
    
    # Преобразуем JSON строку в список строк (зашифрованных блоков)
    json_start = time.time()
    encrypted_blocks_str = json.loads(json_str)
    json_time = time.time() - json_start
    num_blocks = len(encrypted_blocks_str)
    logger.info(f"[GRASSHOPPER DECRYPT] JSON десериализация завершена за {json_time:.4f} сек. Загружено {num_blocks} зашифрованных блоков")
    
    decrypted_bytes = []
    
    # Расшифровываем каждый блок
    decrypt_start = time.time()
    for idx, encrypted_block_str in enumerate(encrypted_blocks_str):
        block_start = time.time()
        block_num = idx + 1
        
        # Преобразуем строку обратно в число
        encrypted_block = int(encrypted_block_str)
        
        # Расшифровываем блок напрямую как число
        decrypted_block_int = _kuznechik_decrypt_int(encrypted_block, _grasshopper_key)
        
        # Преобразуем число обратно в байты (16 байт = 128 бит)
        block_bytes = decrypted_block_int.to_bytes(16, byteorder='big')
        
        decrypted_bytes.append(block_bytes)
        
        block_time = time.time() - block_start
        if block_num % 10 == 0 or block_time > 0.01:
            logger.info(f"[GRASSHOPPER DECRYPT] Расшифрован блок {block_num}/{num_blocks} за {block_time:.4f} сек")
    
    decrypt_time = time.time() - decrypt_start
    logger.info(f"[GRASSHOPPER DECRYPT] Расшифрование {num_blocks} блоков завершено за {decrypt_time:.4f} сек (среднее: {decrypt_time/num_blocks:.6f} сек/блок)")
    
    # Объединяем все блоки
    merge_start = time.time()
    result = b''.join(decrypted_bytes)
    merge_time = time.time() - merge_start
    logger.info(f"[GRASSHOPPER DECRYPT] Объединение блоков завершено за {merge_time:.4f} сек. Размер: {len(result)} байт")
    
    # Удаляем trailing нули (падинг) - только если они были добавлены при шифровании
    strip_start = time.time()
    result = result.rstrip(b'\x00')
    strip_time = time.time() - strip_start
    logger.info(f"[GRASSHOPPER DECRYPT] Удаление паддинга завершено за {strip_time:.4f} сек. Размер после удаления: {len(result)} байт")
    
    # Декодируем в строку
    decode_start = time.time()
    try:
        decoded_result = result.decode("utf-8")
    except UnicodeDecodeError:
        # Если не получается декодировать, пробуем с игнорированием ошибок
        decoded_result = result.decode("utf-8", errors='ignore')
    decode_time = time.time() - decode_start
    total_time = time.time() - start_time
    logger.info(f"[GRASSHOPPER DECRYPT] Декодирование в UTF-8 завершено за {decode_time:.4f} сек. Расшифровано {len(decoded_result)} символов")
    logger.info(f"[GRASSHOPPER DECRYPT] Полное время расшифрования: {total_time:.4f} сек (Base64: {base64_time:.4f}, JSON: {json_time:.4f}, расшифрование: {decrypt_time:.4f}, объединение: {merge_time:.4f}, удаление паддинга: {strip_time:.4f}, декодирование: {decode_time:.4f})")
    
    return decoded_result


__all__ = ['grasshopper_encrypt', 'grasshopper_decrypt', 'kuznechik_encrypt', 'kuznechik_decrypt']
