import time
from functools import lru_cache


@lru_cache(maxsize=5)
def calculate(x):
    return x * 5

print(calculate(1))
print(calculate(2))
print(calculate(3))
print(calculate(1))
print(calculate(2))
print(calculate(3))
print(calculate(1))
print(calculate(2))
print(calculate(3))
print(calculate(1))
print(calculate(2))
print(calculate(3))
print(calculate(1))
print(calculate(2))
print(calculate(3))
print(calculate(1))
print(calculate(2))
print(calculate(3))
print(calculate(1))
print(calculate(2))
print(calculate(3))
print(calculate(1))
print(calculate(2))
print(calculate(3))
print(calculate(1))
print(calculate(2))
print(calculate(3))
print(calculate(1))
print(calculate(2))
print(calculate(3))
