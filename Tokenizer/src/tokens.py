import sys
import gzip
from collections import Counter
import copy
import matplotlib.pyplot as plt
import numpy as np
# Your function start here

if __name__ == '__main__':
    # Read arguments from command line; or use sane defaults for IDE.
    argv_len = len(sys.argv)
    inputFile = sys.argv[1] if argv_len >= 2 else "P1-train.gz"
    outputFilePrefix = sys.argv[2] if argv_len >= 3 else "outPrefix"
    tokenize_type = sys.argv[3] if argv_len >= 4 else "spaces"
    stoplist_type = sys.argv[4] if argv_len >= 5 else "yesStop"
    stemming_type = sys.argv[5] if argv_len >= 6 else "porterStem"
    tokens = []

    # Below is stopword list
    stopword_lst = ["a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
                    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the", "to",
                    "was", "were", "with"]

    vowels = ['a', 'e', 'i', 'o', 'u', 'y']

    def fix_http(t):
        while t[-1] in ',.!?\"\':;<>[]{}\\|+=_-)(*&^%$#@~`':
            t = t[:-1]
        return t

    def space_token(f):
        for line in f:
            cur_tokens = line.strip().split()
            for char in cur_tokens:
                if char != "":
                    tokens.append(char.decode('utf-8'))

    def one_number(t):
        return any(char.isdigit() for char in t)

    def only_digit(t):
        if set(t).issubset(set("0123456789+-,.")) and one_number(t):
            return True
        return False

    def further_process(t):
        h = 0
        while h < len(t):
            if t[h][:7] == "http://" or t[h][:8] == "https://":
                t[h] = fix_http(t[h])
                h += 1
                continue
            if only_digit(t[h]):
                h += 1
                continue
            t[h] = t[h].replace("'", "").replace('"', '')
            t[h] = t[h].replace(",", ":").replace("!", ":").replace("?", ":").replace("\"", ":")\
                .replace("\'", ":").replace(";", ":").replace("<", ":").replace(">", ":").replace("[", ":")\
                .replace("]", ":").replace("{", ":").replace("}", ":").replace("\\", ":").replace("|", ":")\
                .replace("+", ":").replace("=", ":").replace("_", ":").replace("-", ":").replace(")", ":")\
                .replace("(", ":").replace("*", ":").replace("&", ":").replace("^", ":").replace("%", ":")\
                .replace("$", ":").replace("#", ":").replace("@", ":").replace("~", ":").replace("`", ":")\
                .replace("/", ":")
            if t[h] == '':
                t.pop(h)
                h += 1
                continue
            if t[h] != '' and t[h][-1] == ':':
                t[h] = t[h][:-1]
            if t[h] != '' and t[h][0] == ':':
                t[h] = t[h][1:]
            if ':' in t[h]:
                temp = t[h].split(':')
                temp = further_process(temp)
                for f in range(len(temp)):
                    if temp[f] == '':
                        continue
                    t.insert(h + f + 1, temp[f])
                t.pop(h)
                h += 1
                continue
            t[h] = t[h].replace('.', '')
            h += 1
        return t

    def fancy_token():
        i = 0
        while i < len(tokens):
            if tokens[i][:7] == "http://" or tokens[i][:8] == "https://":
                tokens[i] = fix_http(tokens[i])
                i += 1
                continue
            tokens[i] = tokens[i].lower()
            if only_digit(tokens[i]):
                i += 1
                continue
            if "-" in tokens[i]:
                temp = tokens[i].split("-")
                last = ""
                for word in temp:
                    last += word
                temp.append(last)
                temp = further_process(temp)
                if '' in temp:
                    temp.remove('')
                tokens.insert(i + 1, temp)
                tokens.pop(i)
                i += 1
                continue
            tokens[i] = tokens[i].replace("'", "").replace('"', '')
            tokens[i] = tokens[i].replace(",", ":").replace("!", ":").replace("?", ":")\
                .replace("\"", ":").replace("\'", ":").replace(";", ":").replace("<", ":").replace(">", ":")\
                .replace("[", ":").replace("]", ":").replace("{", ":").replace("}", ":").replace("\\", ":")\
                .replace("|", ":").replace("+", ":").replace("=", ":").replace("_", ":").replace("-", ":")\
                .replace(")", ":").replace("(", ":").replace("*", ":").replace("&", ":").replace("^", ":")\
                .replace("%", ":").replace("$", ":").replace("#", ":").replace("@", ":").replace("~", ":")\
                .replace("`", ":").replace("/", ":")
            if tokens[i] != '' and tokens[i][-1] == ":":
                tokens[i] = tokens[i][:-1]
                if tokens[i][:7] == "http://" or tokens[i][:8] == "https://":
                    tokens[i] = fix_http(tokens[i])
                    i += 1
                    continue
                if only_digit(tokens[i]):
                    i += 1
                    continue
            if tokens[i] != '' and tokens[i][0] == ":":
                tokens[i] = tokens[i][1:]
                if tokens[i][:7] == "http://" or tokens[i][:8] == "https://":
                    tokens[i] = fix_http(tokens[i])
                    i += 1
                    continue
                if only_digit(tokens[i]):
                    i += 1
                    continue
            if ':' in tokens[i]:
                temp = tokens[i].split(':')
                temp = further_process(temp)
                if '' in temp:
                    temp.remove('')
                tokens.insert(i + 1, temp)
                tokens.pop(i)
                i += 1
                continue
            tokens[i] = tokens[i].replace('.', '')
            i += 1

    def pre_porter_stem():
        for a in range(len(tokens)):
            if type(tokens[a]) == list:
                for z in range(len(tokens[a])):
                    if tokens[a][z] != '':
                        tokens[a][z] = porter_stem(tokens[a][z])
            elif tokens[a] != '':
                tokens[a] = porter_stem(tokens[a])

    def porter_stem(w):
        if w[-4:] == "sses":
            w = w[:-4] + "ss"
        elif w[-3:] == "ies" or w[-3:] == "ied":
            if len(w[:-3]) > 1:
                w = w[:-3] + 'i'
            else:
                w = w[:-3] + 'ie'
        elif w[-2:] != "us" and w[-2:] != "ss":
            if w[-1] == "s" and any(s in vowels for s in w[:-2]):
                w = w[:-1]
        if w[-3:] == "eed":
            if w[-4] not in vowels and any(s in vowels for s in w[:-4]):
                w = w[:-3] + 'ee'
        elif w[-5:] == "eedly":
            if w[-6] not in vowels and any(s in vowels for s in w[:-6]):
                w = w[:-5] + 'ee'
        elif w[-2:] == "ed":
            if any(s in vowels for s in w[:-2]):
                w = w[:-2]
                if w[-2:] == "at" or w[-2:] == "bl" or w[-2:] == "iz":
                    w += 'e'
                elif w[-2:] in ["bb", "dd", "ff", "gg", "mm", "nn", "pp", "rr", "tt"]:
                    w = w[:-1]
                elif len(w) == 2 and w[0] in vowels and w[1] not in vowels:
                    w += 'e'
                elif w[-1] not in vowels and w[-1] != 'w' and w[-1] != 'x' and \
                        w[-2] in vowels and all(s not in vowels for s in w[:-2]):
                    w += 'e'
        elif w[-3:] == "ing":
            if any(s in vowels for s in w[:-3]):
                w = w[:-3]
                if w[-2:] == "at" or w[-2:] == "bl" or w[-2:] == "iz":
                    w += 'e'
                elif w[-2:] in ["bb", "dd", "ff", "gg", "mm", "nn", "pp", "rr", "tt"]:
                    w = w[:-1]
                elif len(w) == 2 and w[0] in vowels and w[1] not in vowels:
                    w += 'e'
                elif w[-1] not in vowels and w[-1] != 'w' and w[-1] != 'x' \
                        and w[-2] in vowels and all(s not in vowels for s in w[:-2]):
                    w += 'e'
        elif w[-4:] == "edly":
            if any(s in vowels for s in w[:-4]):
                w = w[:-4]
                if w[-2:] == "at" or w[-2:] == "bl" or w[-2:] == "iz":
                    w += 'e'
                elif w[-2:] in ["bb", "dd", "ff", "gg", "mm", "nn", "pp", "rr", "tt"]:
                    w = w[:-1]
                elif len(w) == 2 and w[0] in vowels and w[1] not in vowels:
                    w += 'e'
                elif w[-1] not in vowels and w[-1] != 'w' and w[-1] != 'x' \
                        and w[-2] in vowels and all(s not in vowels for s in w[:-2]):
                    w += 'e'
        elif w[-5:] == "ingly":
            if any(s in vowels for s in w[:-5]):
                w = w[:-5]
                if w[-2:] == "at" or w[-2:] == "bl" or w[-2:] == "iz":
                    w += 'e'
                elif w[-2:] in ["bb", "dd", "ff", "gg", "mm", "nn", "pp", "rr", "tt"]:
                    w = w[:-1]
                elif len(w) == 2 and w[0] in vowels and w[1] not in vowels:
                    w += 'e'
                elif w[-1] not in vowels and w[-1] != 'w' and w[-1] != 'x' and \
                        w[-2] in vowels and all(s not in vowels for s in w[:-2]):
                    w += 'e'
        if len(w) > 2 and w[-1] == "y" and w[-2] not in vowels:
            w = w[:-1] + "i"
        return w

    def make_heap():
        unique = []
        with open(outputFilePrefix + "-heaps.txt", 'w') as f:
            for i in range(len(non_list_form)):
                if non_list_form[i] not in unique:
                    unique.append(non_list_form[i])
                if (i + 1) % 10 == 0:
                    f.write(str(i + 1) + " " + str(len(unique)) + '\n')
                elif i == len(non_list_form) - 1:
                    f.write(str(i + 1) + " " + str(len(unique)) + '\n')
        return len(unique)

    def make_stat(n):
        with open(outputFilePrefix + "-stats.txt", 'w') as f:
            f.write(str(len(non_list_form)) + '\n' + str(n) + '\n')
            b = sorted(non_list_form)
            occur = [item for items, c in Counter(b).most_common() for item in [items] * c]
            cur_count_1 = 0
            word_count = 0
            for i in range(len(occur)):
                if word_count == 100:
                    break
                if i == len(occur) - 1:
                    f.write(occur[i] + " " + str(cur_count_1 + 1) + '\n')
                    continue
                if occur[i] != occur[i + 1]:
                    f.write(occur[i] + " " + str(cur_count_1 + 1) + '\n')
                    cur_count_1 = 0
                    word_count += 1
                else:
                    cur_count_1 += 1

    def remove_list():
        lst = []
        for a in range(len(tokens)):
            if type(tokens[a]) == list:
                for b in range(len(tokens[a])):
                    if tokens[a][b] != '':
                        lst.append(tokens[a][b])
            elif tokens[a] != '':
                lst.append(tokens[a])
        return lst

    def create_tokens():
        with open(outputFilePrefix + "-tokens.txt", 'w') as f:
            for i in range(len(copy)):
                f.write(copy[i])
                if type(tokens[i]) == list:
                    for a in range(len(tokens[i])):
                        if tokens[i][a] != '':
                            f.write(" " + tokens[i][a])
                elif tokens[i] != '':
                    f.write(" " + tokens[i])
                f.write('\n')

    def heaps_law(word_list):
        vocabulary = set()
        word_count = []
        vocab_count = []

        for i, word in enumerate(word_list):
            vocabulary.add(word)
            word_count.append(i+1)
            vocab_count.append(len(vocabulary))

        return word_count, vocab_count


    with gzip.open(inputFile, "r") as file:
        if tokenize_type == "spaces":
            space_token(file)
            copy = tokens.copy()
        else:
            space_token(file)
            copy = tokens.copy()
            fancy_token()
        if stoplist_type == "yesStop":
            for tok in range(len(tokens)):
                if type(tokens[tok]) == list:
                    for i in range(len(tokens[tok])):
                        if tokens[tok][i] in stopword_lst:
                            tokens[tok][i] = ''
                elif tokens[tok] in stopword_lst:
                    tokens[tok] = ''
        if stemming_type == "porterStem":
            pre_porter_stem()
        non_list_form = remove_list()
        num_unique = make_heap()
        make_stat(num_unique)
        word_count, vocab_count = heaps_law(non_list_form)
        plt.plot(word_count, vocab_count)
        plt.xlabel('Words in Collection')
        plt.ylabel('Words in Vocabulary')
        plt.title("Heap's Law")
        plt.savefig('heaps.jpg')
        create_tokens()
