from struct import pack
from struct import unpack

from .const import BLOCKSIZE, Pi, Tau, A, C
from .utils import hexdec, hexenc, strxor


def add512bit(a, b):
    a = bytearray(a)
    b = bytearray(b)
    cb = 0
    res = bytearray(64)
    for i in range(64):
        cb = a[i] + b[i] + (cb >> 8)
        res[i] = cb & 0xFF
    return res


def g(n, hsh, msg):
    res = E(LPS(strxor(hsh[:8], pack("<Q", n)) + hsh[8:]), msg)
    return strxor(strxor(res, hsh), msg)


def E(k, msg):
    for i in range(12):
        msg = LPS(strxor(k, msg))
        k = LPS(strxor(k, C[i]))
    return strxor(k, msg)


def LPS(data):
    return L(PS(bytearray(data)))


def PS(data):
    res = bytearray(BLOCKSIZE)
    for i in range(BLOCKSIZE):
        res[Tau[i]] = Pi[data[i]]
    return res


def L(data):
    res = []
    for i in range(8):
        val = unpack("<Q", data[i * 8 : i * 8 + 8])[0]
        res64 = 0
        for j in range(BLOCKSIZE):
            if val & 0x8000000000000000:
                res64 ^= A[j]
            val <<= 1
        res.append(pack("<Q", res64))
    return b"".join(res)

def stribog_hex_to_str(data: bytes, stribog_size: int = 512) -> str:
    return "".join(
        reversed([("%0.2X" % a) for a in data][: (32 if stribog_size == 256 else 64)])
    )
def str_to_hexstr(data: str) -> str:
    hexstr = "".join([str(ord(c)) for c in data])
    if len(hexstr) % 2 != 0:
        hexstr += "0"
    return hexstr

class Stribog(object):
    block_size = BLOCKSIZE

    def __init__(self, data=b"", digest_size=512):
        self.digest_size = digest_size
        self.data = data

    def update(self, data):
        self.data += data

    def digest(self):
        hsh = BLOCKSIZE * (b"\x01" if self.digest_size == 256 else b"\x00")
        chk = BLOCKSIZE * b"\x00"
        n = 0
        data = self.data
        for i in range(0, len(data) // BLOCKSIZE * BLOCKSIZE, BLOCKSIZE):
            block = data[i : i + BLOCKSIZE]
            hsh = g(n, hsh, block)
            chk = add512bit(chk, block)
            n += 512

        padblock_size = len(data) * 8 - n
        data += b"\x01"
        padlen = BLOCKSIZE - len(data) % BLOCKSIZE
        if padlen != BLOCKSIZE:
            data += b"\x00" * padlen

        hsh = g(n, hsh, data[-BLOCKSIZE:])
        n += padblock_size
        chk = add512bit(chk, data[-BLOCKSIZE:])
        hsh = g(0, hsh, pack("<Q", n) + 56 * b"\x00")
        hsh = g(0, hsh, chk)
        if self.digest_size == 256:
            return hsh[32:]
        return hsh

    def hexdigest(self):
        return hexenc(self.digest())
