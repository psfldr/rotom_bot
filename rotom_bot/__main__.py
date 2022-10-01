import sys

from rotom_bot.rotom_bot import fib

if __name__ == "__main__":
    n = int(sys.argv[1])
    print(fib(n))
