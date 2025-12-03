"""
Модуль генерации больших простых чисел.
"""

import random
from time import time
from typing import Generator
import sys


sys.set_int_max_str_digits(0)


def __linear_congruental_generator(x: int) -> Generator[int, int, int]:
    """
    Генератор лийненого конгруэнтного метода
    x: int - начальное генерируемое число (обычно - энтропия)
    """
    a, c, m = 1103515245, 12345, 2**31
    while True:
        x = (a * x + c) % m
        yield x


def rndint(l: int, r: int) -> Generator[int, int, int]:
    """
    Метод генерации случайного числа через линейный конгруэнтный метод
    r: int - левая граница
    l: int - правая граница
    """
    while True:
        seed = int(str(time()).split(".")[1]) // 100
        rand = __linear_congruental_generator(seed)
        next(rand)
        yield round(l + (next(rand) % (r - l + 1)))


def is_prime(n: int, k: int = 5) -> bool:
    """
    Метод проверки числа n на простоту через тест Миллера-Рабина
    n: int - тестируемое число
    k: int - кол-во тестов
    """
    if n <= 1:
        return False
    elif n <= 3:
        return True
    elif n % 2 == 0:
        return False

    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1

    for _ in range(k):
        rnd_gen = rndint(2, n - 2)
        a = next(rnd_gen)
        x = pow(a, d, n)

        if x == 1 or x == n - 1:
            continue

        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False

    return True


def generate_candidate(bits: int):
    """Генерация кандидата на простое число"""
    candidate_prime = 1

    candidate_prime |= 1 << (bits - 1)
    candidate_prime |= 1

    rnd_gen = rndint(0, 1)

    for i in range(1, bits - 1):
        if next(rnd_gen) == 1:
            candidate_prime |= 1 << i

    return candidate_prime


def generate_large_prime(bits: int = 1024, k: int = 40) -> int:
    """
    Генерирует простое число заданной битовой длины.
    bits: int - количество бит
    test_count: int - количество итераций теста Миллера-Рабина
    max_attempts: int - кол-во попыток генерации
    """
    while True:
        l_prime = generate_candidate(bits)
        if is_prime(l_prime):
            return l_prime
        else:
            return False


if __name__ == "__main__":
    a = generate_large_prime(2048)
    print(a)
