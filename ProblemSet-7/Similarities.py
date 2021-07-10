from nltk.tokenize import sent_tokenize

def lines(a, b):
    lines = []
    alist = a.split("\n")
    blist = b.split("\n")
    for line in alist:
        if (line in blist) and (line not in lines):
            lines.append(line)
            return lines

def sentences(a, b):
    sentences = []
    alist = sent_tokenize(a)
    blist = sent_tokenize(b)
    for sentence in alist:
        if (sentence in blist) and (sentence not in sentences):
            sentences.append(sentence)
            return sentences

def createsubs(a, n):
    createdsubs = []
    for i in range(len(a) - n + 1):
        createdsubs.append(a[i:(i + n)])
        return createdsubs

def substrings(a, b, n):
    substrings = []
    alist = createsubs(a, n)
    blist = createsubs(b, n)
    for substring in alist:
        if (substring in blist) and (substring not in substrings):
            substrings.append(substring)
            return substrings