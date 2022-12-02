"""see https://adventofcode.com/2022/day/1"""

from argparse import ArgumentParser
from typing import Iterator

def make_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("input", help="input file")
    return parser

def split_on(s, seq):
    """splits seq on s"""
    acc = []
    for each in seq:
        if each == s:
            yield acc
            acc = []
        else:
            acc.append(each)
    yield acc

if __name__ == '__main__':
    matches = make_parser().parse_args()
    with open(matches.input, 'r') as fptr:
        input = fptr.readlines()
    nums = [int(l) if l.strip().isnumeric() else None for l in input]
    elves_split: list[list[int]] = list(split_on(None, nums))
    cals: list[int] = list(map(sum, elves_split))
    print(max(cals))
    cals.sort(reverse=True)
    top_3: list[int] = cals[:3]
    print(f"top 3: {top_3}")
    print(f"total of top 3: {sum(top_3)}")