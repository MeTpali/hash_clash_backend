import json
import base64
from .kuznechik import kuznechik_encrypt, kuznechik_decrypt, DEFAULT_KEY

# Используем ключ по умолчанию для шифрования
_grasshopper_key = DEFAULT_KEY


def grasshopper_encrypt(text: str) -> str:
    """
    Шифрует строку при помощи Kuznechik (Grasshopper).
    Разбивает текст на блоки по 16 байт (128 бит) и шифрует каждый блок.
    Возвращает зашифрованные данные в формате base64 JSON.
    """
    # Разбиваем текст на блоки по 16 байт (128 бит)
    text_bytes = text.encode("utf-8")
    block_size = 16
    
    encrypted_blocks = []
    
    # Обрабатываем текст блоками
    for i in range(0, len(text_bytes), block_size):
        block_bytes = text_bytes[i:i + block_size]
        
        # Дополняем блок до 16 байт нулями, если необходимо
        if len(block_bytes) < block_size:
            block_bytes += b'\x00' * (block_size - len(block_bytes))
        
        # Преобразуем блок байтов в число (128 бит)
        # kuznechik_encrypt делает: int(msg.encode().hex(), 16)
        # Значит нужно передать строку, которая после encode().hex() даст правильный hex
        # Но проще передать уже готовый hex из байтов
        block_int = int.from_bytes(block_bytes, byteorder='big')
        block_hex_str = format(block_int, '032x')  # 32 hex символа для 16 байт
        
        # Шифруем блок - передаем hex строку
        encrypted_block = kuznechik_encrypt(block_hex_str, _grasshopper_key)
        encrypted_blocks.append(str(encrypted_block))  # Преобразуем число в строку для JSON
    
    # Преобразуем список зашифрованных блоков в JSON строку, затем в base64
    json_str = json.dumps(encrypted_blocks)
    return base64.b64encode(json_str.encode("utf-8")).decode("utf-8")


def grasshopper_decrypt(cipher_b64: str) -> str:
    """
    Расшифровывает строку, зашифрованную через grasshopper_encrypt.
    """
    # Декодируем base64 в JSON строку
    json_str = base64.b64decode(cipher_b64).decode("utf-8")
    
    # Преобразуем JSON строку в список строк (зашифрованных блоков)
    encrypted_blocks_str = json.loads(json_str)
    
    decrypted_bytes = []
    
    # Расшифровываем каждый блок
    for encrypted_block_str in encrypted_blocks_str:
        # Преобразуем строку обратно в число
        encrypted_block = int(encrypted_block_str)
        
        # Расшифровываем блок
        # kuznechik_decrypt возвращает строку через bytes.fromhex(hex(dt)[2:]).decode()
        decrypted_hex = kuznechik_decrypt(encrypted_block, _grasshopper_key)
        
        # Преобразуем hex строку в байты
        try:
            block_bytes = bytes.fromhex(decrypted_hex)
        except (ValueError, TypeError):
            # Если что-то пошло не так, попробуем другой способ
            # decrypted_hex может быть уже байтами или числом
            if isinstance(decrypted_hex, str):
                block_bytes = bytes.fromhex(decrypted_hex)
            else:
                # Если это число, преобразуем в hex строку
                hex_str = hex(decrypted_hex)[2:]
                if len(hex_str) % 2 != 0:
                    hex_str = '0' + hex_str
                block_bytes = bytes.fromhex(hex_str)
        
        decrypted_bytes.append(block_bytes)
    
    # Объединяем все блоки
    result = b''.join(decrypted_bytes)
    
    # Удаляем trailing нули (падинг) - только если они были добавлены при шифровании
    # Определяем длину исходного текста по последнему блоку
    # Если последний блок полностью состоит из нулей (кроме возможно одного), удаляем их
    result = result.rstrip(b'\x00')
    
    # Декодируем в строку
    try:
        return result.decode("utf-8")
    except UnicodeDecodeError:
        # Если не получается декодировать, пробуем с игнорированием ошибок
        return result.decode("utf-8", errors='ignore')


__all__ = ['grasshopper_encrypt', 'grasshopper_decrypt', 'kuznechik_encrypt', 'kuznechik_decrypt']
