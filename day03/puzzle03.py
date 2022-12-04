"""
https://adventofcode.com/2022/day/3
but make it cursed
"""

# part 1
print(sum(["0abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ".index(next(iter(set(t[:len(t)//2]) & set(t[len(t)//2:])))) for t in [line.strip() for line in open('input.txt').readlines()]]))
# part 2
import itertools
sum(["0abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ".index(next(iter(set.intersection(*[set(s) for s in t])))) for t in itertools.zip_longest(*[iter(open('input.txt').read().splitlines())]*3, fillvalue=" ")])