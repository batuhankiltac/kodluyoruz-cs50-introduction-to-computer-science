from cs50 import get_float
import math

while True:
    change = get_float("Change owed: ")
    if change >= 0.00:
        break
        q = math.floor(float(change / 0.25))
        qremain = round((float(change % 0.25)), 2)

        d = math.floor(float(qremain / 0.10))
        dremain = round((float(qremain % 0.10)), 2)

        n = math.floor(float(dremain / 0.05))
        premain = round((float(dremain % 0.05)), 2)

        p = int(float(premain / 0.01))

        sum = q + d + n + p

        print("{}\n".format(sum))
