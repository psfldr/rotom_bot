import sys

from aws_test_and_deploy.aws_test_and_deploy import fib

if __name__ == "__main__":
    n = int(sys.argv[1])
    print(fib(n))
