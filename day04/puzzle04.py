"""https://adventofcode.com/2022/day/4"""
from typing import Iterator, Tuple

def make_ranges(lines: list[str]) -> Iterator[Tuple[range, range]]:
    """take a list of lines, each with two assignments deliminted by comma, and make ranges from them"""
    def make_range(s: str) -> range:
        """makes a single range from text like '5-6"""
        (start, end) = s.split('-')
        return range(int(start), int(end)+1)
    for each_line in lines:
        (left, right) = each_line.split(',')
        yield (make_range(left), make_range(right))

def has_subset(range1: range, range2: range) -> bool:
    """returns true if range1 and range2 overlap"""
    sr1 = set(range1)
    sr2 = set(range2)
    return sr1 <= sr2 or sr1 >= sr2

def has_any_overlap(range1: range, range2: range) -> bool:
    """returns true if range1 and range2 have any values in common"""
    sr1 = set(range1)
    sr2 = set(range2)
    return bool(sr1 & sr2)

if __name__ == '__main__':
    with open('input.txt') as fptr:
        lines = fptr.read().splitlines()
    ranges = list(make_ranges(lines))
    overlap = [(r1, r2) for (r1, r2) in ranges if has_subset(r1, r2)]
    print(f"ranges with total overlap: {len(overlap)}")
    any_overap = [(r1, r2) for (r1, r2) in ranges if has_any_overlap(r1, r2)]
    print(f"ranges with any numbers in common: {len(any_overap)}")