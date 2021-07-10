from sys import argv, exit
from cs50 import get_string

if len(argv) != 2:
    exit("Usage: python caesar.py k")
    key = int(argv[1])
    plaintext = get_string("plaintext: ")
    print("ciphertext: ", end="")
    for p in plaintext:
        if p.isalpha():
            upper = p.upper()
            alphabeticalindex = ord(upper) - 65
            result = 65 + ((alphabeticalindex + key) % 26)
            if p.islower():
                c = chr(result).lower()
            else:
                c = chr(result)
        else:
            c = p
            print(c, end="")
            print("")