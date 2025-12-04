from core.utils.kuznechik import kuznechik_encrypt, kuznechik_decrypt

if __name__ == "__main__":
    msg = "1122334455667700ffeeddccbbaa9988"
    msg = int("1122334455667700ffeeddccbbaa9988", 16)
    print(f"Исходное сообщение (int): {msg}")
    print(f"Исходное сообщение (hex): {hex(msg)}")
    k = int("8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef", 16)
    
    CT = kuznechik_encrypt(msg, k)
    print(f"Зашифрованное сообщение (hex): {hex(CT)}")
    DT = kuznechik_decrypt(CT, k, return_type='int')

    print(f"Расшифрованное сообщение (int): {DT}")
    print(f"Расшифрованное сообщение (hex): {hex(DT)}")
    print(f"Сообщения совпадают: {msg == DT}")
