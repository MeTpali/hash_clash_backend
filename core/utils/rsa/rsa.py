
from .keygen import generate_rsa

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
    

    def encrypt(self, message: str) -> list[int]:
        return [pow(ord(m), self.e, self.n) for m in message]
    
    def decrypt(self, cypher: list[int]) -> list[str]:
        return "".join([chr(pow(c, self.d, self.n)) for c in cypher])
    


if __name__ == '__main__':
    rsa = RSA()
    rsa.gen_keys(32768)
    msg = "hello"
    
    cpr = rsa.encrypt(msg)
    print(msg)
    print(cpr)
    print(rsa.decrypt(cpr))
