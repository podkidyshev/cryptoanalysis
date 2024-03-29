from math import gcd

from sys import argv

from prime import factorize


def f(x, n):
    return (pow(x, 2, n) + 1) % n


def p_pollard(n, c):
    c = c % n
    a = b = c
    values = {c}
    a = f(a, n)
    b = f(f(b, n), n)
    while True:
        d = gcd((a - b) % n, n)
        if 1 < d < n:
            return d
        elif d == n:
            return -1
        a = f(a, n)
        b = f(f(b, n), n)
        if a in values or b in values:
            return -1


def main():
    if len(argv) == 1:
        n = int(input('Введите n = '))
        c = int(input('Введите с = ')) % n
        assert 1 < c < n, 'c должно быть 1 < c < n'
    elif len(argv) == 2:
        n = int(argv[1])
        c = int(input('Введите с = ')) % n
    else:
        n = int(argv[1])
        c = int(argv[2]) % n
    assert 1 < c < n, 'c должно быть 1 < c < n'

    factors = factorize(n, p_pollard, c)
    print('\n'.join(map(str, factors.items())))


if __name__ == '__main__':
    main()
