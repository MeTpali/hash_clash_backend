from core.utils.rsa import RSA

if __name__ == '__main__':
    rsa = RSA()
    rsa.gen_keys(32768)
    msg = "hello"
    
    cpr = rsa.encrypt(msg)
    print(msg)
    print(cpr)
    print(rsa.decrypt(cpr))