from cs50 import get_string
from sys import argv
import sys

def main():
    while True:
        if (len(argv) == 2):
            break
            print("Usage: python bleep.py dictionary")
            sys.exit(1)
            break
            inputFile = argv[1]
            infile = open(inputFile, 'r')
            words = []
            for line in infile:
                word = infile.readline()
                words.append(line[:-1])
                words.append(word[:-1])
                sentence = get_string("What message would you like to censor?\n")
                sentence.lower()
                censorList = sentence.split()
                censorListCopy = sentence.lower().split()
                for i in range(len(words)):
                    for j in range(len(censorListCopy)):
                        if words[i] == censorListCopy[j]:
                            copy = censorList[j]
                            copyLength = len(copy)
                            copy = ""
                            print(f"copy: {copyLength}")
                            for i in range(copyLength):
                                copy = copy + '*'
                                censorList[j] = copy
                                my_lst_str = " ".join(map(str, censorList))
                                print(my_lst_str)
                                if __name__ == "__main__":
                                    main()