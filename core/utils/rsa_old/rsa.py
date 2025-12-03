import time
import logging
from .keygen import generate_rsa

logger = logging.getLogger(__name__)

class RSA:

    def gen_keys(self, length: int = 2048):
        rsa = generate_rsa(length)
        self.e = rsa["public_key"][0]
        self.n = rsa["public_key"][1]
        self.d = rsa["private_key"][0]


    def set_keys(self, public_key: tuple[int, int], private_key:  tuple[int, int]):
        self.e = public_key[0]
        self.n = public_key[1]
        self.d = private_key[0]
        logger.info(f"[RSA] Ключи установлены. Размер модуля n: {len(str(self.n))} цифр")
    

    def encrypt(self, message: str) -> list[int]:
        """
        Шифрует сообщение посимвольно.
        Каждый символ шифруется отдельно через pow(ord(m), self.e, self.n)
        """
        encrypt_start = time.time()
        logger.info(f"[RSA.encrypt] Начало шифрования {len(message)} символов")
        
        result = []
        for i, m in enumerate(message):
            char_start = time.time()
            encrypted = pow(ord(m), self.e, self.n)
            char_time = time.time() - char_start
            
            # Логируем каждый 100-й символ или если символ обрабатывается долго (>0.1 сек)
            if (i + 1) % 100 == 0 or char_time > 0.1:
                logger.info(f"[RSA.encrypt] Зашифрован символ {i+1}/{len(message)} за {char_time:.4f} сек")
            
            result.append(encrypted)
        
        total_time = time.time() - encrypt_start
        logger.info(f"[RSA.encrypt] Все {len(message)} символов зашифрованы за {total_time:.4f} сек (среднее: {total_time/len(message):.6f} сек/символ)")
        return result
    
    def decrypt(self, cypher: list[int]) -> str:
        """
        Расшифровывает список чисел посимвольно.
        Каждое число расшифровывается через pow(c, self.d, self.n) - это медленная операция!
        """
        decrypt_start = time.time()
        logger.info(f"[RSA.decrypt] Начало расшифрования {len(cypher)} символов. ВНИМАНИЕ: это может занять много времени!")
        
        result = []
        for i, c in enumerate(cypher):
            char_start = time.time()
            decrypted = pow(c, self.d, self.n)  # Это медленная операция - возведение в большую степень!
            char_time = time.time() - char_start
            
            # Логируем каждый 10-й символ или если символ обрабатывается долго (>0.1 сек)
            if (i + 1) % 10 == 0 or char_time > 0.1:
                logger.info(f"[RSA.decrypt] Расшифрован символ {i+1}/{len(cypher)} за {char_time:.4f} сек")
            
            result.append(chr(decrypted))
        
        total_time = time.time() - decrypt_start
        logger.info(f"[RSA.decrypt] Все {len(cypher)} символов расшифрованы за {total_time:.4f} сек (среднее: {total_time/len(cypher):.6f} сек/символ)")
        return "".join(result)
    


if __name__ == '__main__':
    rsa = RSA()
    rsa.gen_keys(32768)
    msg = "hello"
    
    cpr = rsa.encrypt(msg)
    print(msg)
    print(cpr)
    print(rsa.decrypt(cpr))
