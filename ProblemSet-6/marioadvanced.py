from cs50 import get_int


def main():
    n = get_int("Enter a number between 1 and 8:\n")
    while n < 1 or n > 8:
        n = get_int("Enter a number between 1 and 8:\n")
        for i in range(n):
            spaces(n, i)
            hashes(i)
            print(" ", end="")
            hashes(i)
            print()


def spaces(n, i):
    for j in range(n, i + 1, -1):
        print(" ", end="")


def hashes(i):
    for k in range(0, i + 1):
        print("#", end="")


main()
