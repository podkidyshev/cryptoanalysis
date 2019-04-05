from itertools import product

from utils import *
from cyphers import Vigenere as Vig, text_to_words, frequencies, Replacement as Rep


CHARS_TO_ATTACK = 3


def attack_text(enc, freqs, length):
    alph = ''.join(sorted(freqs))

    cols = [{"idxs": []} for _ in range(length)]
    for idx, char in enumerate(enc):
        if char in alph:
            cols[idx % length]["idxs"].append(char)

    for col_idx, col in enumerate(cols):
        col_freqs = frequencies(col["idxs"], alph)
        col_freqs = ''.join(k for k, v in col_freqs)
        col["freqs"] = col_freqs

        col["keys"] = []
        for key in Rep.attack_shift(freqs, col_freqs, CHARS_TO_ATTACK):
            col["keys"].append(alph[alph.index(key[0])])

    groups = [col["keys"] for col in cols]
    for item in groups:
        print(item)

    keys = []
    for comb in product(*groups):
        key = ''.join(comb)
        keys.append(key)
    return keys


def frequencies_words(text):
    words = text_to_words(text)
    freqs = {}
    for word in words:
        freqs[word] = freqs.get(word, 0) + 1
    # freqs = {word: words.count(word) for word in set(words)}
    freqs = {word: word_count / len(words) for word, word_count in freqs.items() if word_count > 1}
    freqs = list(sorted(freqs.items(), key=lambda pair: pair[1], reverse=True))
    return freqs[:1000]


def a2_decrypt_char(idx, char, key, alph):
    if key[idx % len(key)] == '*':
        return '*'
    else:
        return Vig.decrypt_char(alph, idx, char, key)


def a2_decrypt(enc, key, alph):
    dec = ''
    for idx, char in enumerate(enc):
        dec += a2_decrypt_char(idx, char, key, alph)
    return dec


def a2(enc, alph, length, word):
    f = get_file_write('bruted2.txt')
    for idx_start in range(len(enc) - len(word)):
        if not all(map(lambda char: char in alph, enc[idx_start:idx_start + len(word)])):
            continue

        key = ''.join([alph[(alph.index(enc[idx + idx_start]) - alph.index(c)) % len(alph)] for idx, c in enumerate(word[:length])])
        key += '*' * (length - len(key))

        if len(word) > length:
            enc_word = enc[idx_start: idx_start + len(word)]
            word_dec = a2_decrypt(enc_word, key, alph)
            if word_dec != word:
                continue

        for _ in range(idx_start % length):
            key = key[-1] + key[:-1]

        f.write('КЛЮЧ: {}\n{}\n\n'.format(key, a2_decrypt(enc, key, alph)))
    f.close()


def main():
    op = argv[1]

    if op == 'freq':
        text = read(argv[2]).lower()
        alph = read(argv[3])
        freqs = frequencies(text, alph)
        freqs = map(lambda pair: '{} : {:.4f}'.format(*pair), freqs)
        write(argv[4], '\n'.join(freqs))
    elif op == 'enc':
        msg = read(argv[2]).lower()
        key = read_text(argv[3])[0]
        alph = read(argv[4])
        enc = Vig.encrypt(msg.lower(), alph, key)
        write('enc.txt', enc)
    elif op == 'dec':
        enc = read(argv[2])
        key = read(argv[3])
        alph = read(argv[4])
        dec = Vig.decrypt(enc, alph, key)
        write('dec.txt', dec)
    elif op == 'at':
        enc = read(argv[2])
        freqs = map(lambda pair: pair.split(':'), read(argv[3]).split('\n'))
        freqs = ''.join(k[0] for k, v in freqs)
        length = int(argv[4])
        keys = attack_text(enc, freqs, length)
        write('keys.txt', '\n'.join(keys))
    elif op == 'brute':
        enc = read(argv[2])
        keys = read(argv[3]).split('\n')
        alph = read(argv[4])
        f = get_file_write('bruted.txt')
        for key in keys:
            f.write('КЛЮЧ : {}\n{}\n\n'.format(key, Vig.decrypt(enc, alph, key)))
            f.write('-------------------------------\n')
        f.close()
    elif op == 'freq2':
        text = '\n'.join(map(lambda arg: read(arg).lower(), argv[2:]))
        freqs = frequencies_words(text)
        freqs = map(lambda pair: '{} : {:.4f}'.format(*pair), freqs)
        write('freq2.txt', '\n'.join(freqs))
    else:
        print('ОШИБКА: неверный код операции')


if __name__ == '__main__':
    main()
