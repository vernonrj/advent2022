"""https://adventofcode.com/2022/day/13"""

import argparse
import json
from typing import Any, Iterable, Iterator, Tuple


def parse_input(lines: Iterable[str]) -> Iterator[Tuple[list[list | int], list[list | int]]]:
    """parses input into an iterator of nested lists"""
    lines = iter(lines)
    while (first := next(lines, None)) and (second := next(lines, None)):
        blank = next(lines, "") # we also need to pull the blank line, but it's optional
        assert not blank.strip(), f"third line should be blank!"
        yield (json.loads(first), json.loads(second))

def fancy_zip(left: list[list | int], right: list[list | int]) -> Iterator[Tuple[int | None, int | None]]:
    """does a zip operation that also does type coercion according to the aoc instructions"""
    left = iter(left)
    right = iter(right)
    while True:
        left_elem = next(left, None)
        right_elem = next(right, None)
        match (left_elem, right_elem):
            case (None, None):
                # this is a terminating condition
                return
            case (None, _) | (_, None) as tup:
                # this is a terminating condition
                yield tup
                return
            case ([*l], [*r]):
                # both values are lists
                for (l, r) in fancy_zip(l, r):
                    match (l, r):
                        case (None, None):
                            # lists were the same length
                            continue
                        case (None, _) | (_, None):
                            # terminating condition
                            yield (l, r)
                            return
                    yield (l, r)
            case ([*l], r):
                # exactly one value is integer
                assert isinstance(r, int)
                for (l, r) in fancy_zip(l, [r]):
                    match (l, r):
                        case (None, None):
                            # lists were the same length
                            continue
                        case (None, _) | (_, None):
                            # terminating condition
                            yield (l, r)
                            return
                    yield (l, r)
            case (l, [*r]):
                # exactly one value is integer
                assert isinstance(l, int)
                for (l, r) in fancy_zip([l], r):
                    match (l, r):
                        case (None, None):
                            # lists were the same length
                            continue
                        case (None, _) | (_, None):
                            # terminating condition
                            yield (l, r)
                            return
                    yield (l, r)
            case (l, r): # default
                # both values are integers
                yield (l, r)

def is_ordered(left_packet: list[list | int], right_packet: list[list | int]) -> bool:
    """returns True if left and right packets are in-order"""
    for (left_elem, right_elem) in fancy_zip(left_packet, right_packet):
        match (left_elem, right_elem):
            case (None, None):
                # end of input but this shouldn't happen.
                raise AssertionError("this shouldn't happen")
            case (None, r):
                # left list ran out of items first. inputs are in the right order
                return True
            case (l, None):
                # right list ran out of items first. inputs are wrong order
                return False
            case (l, r) if l < r:
                # left integer is lower than right integer. inputs are in the right order
                return True
            case (l, r) if l > r:
                # left integer is not lwer than right integer. wrong order
                return False
            case (l, r) if l == r:
                # integers are equal. continue checking
                continue
            case (l, r):
                raise AssertionError("we shouldn't be here")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file to pull from")
    matches = parser.parse_args()
    with open(matches.input) as fptr:
        packets = list(parse_input(fptr.read().splitlines()))
        ordered = [i for (i, (l, r)) in enumerate(packets, start=1) if is_ordered(l, r)]
        print(f"ordered: {ordered}")
        print(f"sum of indices: {sum(ordered)}")