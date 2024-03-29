from itertools import product

from utils import *
from cyphers import text_to_words, get_freqs, read_freqs, exec_freqs
import cyphers.vigenere as vig
import cyphers.replacement as rep


CHARS_TO_ATTACK = 4


def attack_text(enc, freqs, alph, length):
    cols = [{"idxs": []} for _ in range(length)]
    for idx, char in enumerate(enc):
        if char in alph:
            cols[idx % length]["idxs"].append(char)

    for col_idx, col in enumerate(cols):
        col["freqs"] = get_freqs(col["idxs"], alph)

        col["keys"] = []
        for key in rep.attack_shift(freqs, col["freqs"], alph, CHARS_TO_ATTACK):
            col["keys"].append(key)
        col["keys"] = list(map(int, col["keys"][1:]))

    groups = [col["keys"] for col in cols]
    for item in groups:
        print(item)

    keys = []
    keys_set = set()
    for count in range(1, max(map(lambda group: len(group), groups))):
        for comb in product(*list(map(lambda x: x[:count], groups))):
            key = ''.join(map(lambda x: alph[x], comb))
            if key not in keys_set:
                keys.append(key)
                keys_set.add(key)
    return keys


def frequencies_words(text):
    words = text_to_words(text)
    freqs = {}
    for word in words:
        freqs[word] = freqs.get(word, 0) + 1
    freqs = {word: word_count / len(words) for word, word_count in freqs.items() if word_count > 1 and len(word) > 2}
    freqs = list(sorted(freqs.items(), key=lambda pair: pair[1], reverse=True))
    return freqs[:1000]


def a2_decrypt_char(idx, char, key, alph):
    if key[idx % len(key)] == '*':
        return '*'
    else:
        return vig.decrypt_char(alph, idx, char, key)


def a2_decrypt(enc, key, alph):
    dec = ''
    for idx, char in enumerate(enc):
        dec += a2_decrypt_char(idx, char, key, alph)
    return dec


def attack_word(enc, alph, length, word, fin=None):
    f = get_file_write('bruted_word.txt') if fin is None else fin
    keys = set()
    for idx_start in range(len(enc) - len(word)):
        if not all(map(lambda char: char in alph, enc[idx_start:idx_start + len(word)])):
            continue

        key = ''.join([alph[(alph.index(enc[idx + idx_start]) - alph.index(c)) % len(alph)]
                       for idx, c in enumerate(word[:length])])
        key += '*' * (length - len(key))

        if len(word) > length:
            enc_word = enc[idx_start: idx_start + len(word)]
            word_dec = a2_decrypt(enc_word, key, alph)
            if word_dec != word:
                continue

        for _ in range(idx_start % length):
            key = key[-1] + key[:-1]

        if key in keys:
            continue
        keys.add(key)

        f.write('КЛЮЧ: {}\n{}\n\n'.format(key, a2_decrypt(enc, key, alph)))
    if fin is None:
        f.close()


def main():
    if op == 'freq':
        exec_freqs()
    elif op == 'enc':
        vig.exec_encrypt()
    elif op == 'dec':
        vig.exec_decrypt()
    elif op == 'af':
        enc = read(argv[2])
        freqs = read_freqs(argv[3])
        alph = read(argv[4])
        length = int(argv[5])
        keys = attack_text(enc, freqs, alph, length)
        write('keys.txt', '\n'.join(keys))
    elif op == 'brute':
        vig.exec_brute()
    elif op == 'freqw':
        text = '\n'.join(map(lambda arg: read(arg).lower(), argv[2:]))
        freqs = frequencies_words(text)
        freqs = map(lambda pair: '{} : {:.4f}'.format(*pair), freqs)
        write('words.txt', '\n'.join(freqs))
    elif op == 'aw':
        enc = read(argv[2])
        alph = read(argv[3])
        length = int(argv[4])
        word = argv[5]
        if not all(c in alph for c in word):
            print('ОШИБКА: все символы слова должны быть в алфавите')
            exit(1)
        attack_word(enc, alph, length, word)
    else:
        print_wrong_op()


if __name__ == '__main__':
    main()
