from .const import pi, pi_inv

DEFAULT_KEY = int("8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef", 16)

def S(x):
    y = 0
    for i in reversed(range(16)):
        y <<= 8
        y ^= pi[(x >> (8 * i)) & 0xFF]
    return y


def S_inv(x):
    y = 0
    for i in reversed(range(16)):
        y <<= 8
        y ^= pi_inv[(x >> (8 * i)) & 0xFF]
    return y

def multiply_ints_as_polynomials(x, y):
    if x == 0 or y == 0:
        return 0
    z = 0
    while x != 0:
        if x & 1 == 1:
            z ^= y
        y <<= 1
        x >>= 1
    return z

def number_bits(x):
    nb = 0
    while x != 0:
        nb += 1
        x >>= 1
    return nb

def mod_int_as_polynomial(x, m):
    nbm = number_bits(m)
    while True:
        nbx = number_bits(x)
        if nbx < nbm:
            return x
        mshift = m << (nbx - nbm)
        x ^= mshift


def kuznechik_multiplication(x, y):
    z = multiply_ints_as_polynomials(x, y)
    m = int("111000011", 2)
    return mod_int_as_polynomial(z, m)


def kuznechik_linear_functional(x):
    C = [148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148, 1]
    y = 0
    while x != 0:
        y ^= kuznechik_multiplication(x & 0xFF, C.pop())
        x >>= 8
    return y


def R(x):
    a = kuznechik_linear_functional(x)
    return (a << 8 * 15) ^ (x >> 8)


def R_inv(x):
    a = x >> 15 * 8
    x = (x << 8) & (2**128 - 1)
    b = kuznechik_linear_functional(x ^ a)
    return x ^ b

def L(x):
    for _ in range(16):
        x = R(x)
    return x

def L_inv(x):
    for _ in range(16):
        x = R_inv(x)
    return x

def kuznechik_key_schedule(k):
    keys = []
    a = k >> 128
    b = k & (2**128 - 1)
    keys.append(a)
    keys.append(b)
    for i in range(4):
        for j in range(8):
            c = L(8 * i + j + 1)
            (a, b) = (L(S(a ^ c)) ^ b, a)
        keys.append(a)
        keys.append(b)
    return keys


def kuznechik_encrypt(msg: str, k: int | None = DEFAULT_KEY):
    x = int(msg.encode().hex(), 16)
    keys = kuznechik_key_schedule(k)
    for round in range(9):
        x = L(S(x ^ keys[round]))
    return x ^ keys[-1]

def kuznechik_decrypt(x, k):
    keys = kuznechik_key_schedule(k)
    keys.reverse()
    for round in range(9):
        x = S_inv(L_inv(x ^ keys[round]))
    dt = x ^ keys[-1]
    return bytes.fromhex(hex(dt)[2:]).decode()


if __name__ == "__main__":
    msg = "1122334455667700ffeeddccbbaa9988"
    msg = int("1122334455667700ffeeddccbbaa9988", 16)
    print(msg)
    k = int("8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef", 16)
    
    CT = kuznechik_encrypt(msg, k)
    print(hex(CT))
    DT = kuznechik_decrypt(CT, k)

    print(msg == DT)
    print(DT)
