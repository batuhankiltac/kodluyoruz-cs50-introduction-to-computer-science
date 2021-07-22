from sys import argv, exit
from cs50 import get_string

if len(argv) != 2 or argv[1].isalpha() == False:
    exit("Usage: python vigenere.py k")
    keyword = argv[1].upper()
    counter = 0
    plaintext = get_string("plaintext: ")
    print("ciphertext: ", end="")
    for p in plaintext:
        if p.isalpha():
            numkey = ord(keyword[counter % len(keyword)]) - 65
            upper = p.upper()
            alphabeticalindex = ord(upper) - 65
            result = 65 + ((alphabeticalindex + numkey) % 26)
            if p.islower():
                c = chr(result).lower()
            else:
                c = chr(result)
                counter += 1
        else:
            c = p
            print(c, end="")
            print("")
