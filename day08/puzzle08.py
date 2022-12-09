"""https://adventofcode.com/2022/day/8"""
from typing import Iterator, Tuple

def parse_text(text: str) -> list[list[int]]:
    return [[int(x) for x in y] for y in text.splitlines()]

def not_visible_2d(nums: list[list[int]]) -> Tuple[int, int, int]:
    """returns indexes of `nums` that are not "visible" from the outside"""
    for (colidx, col) in enumerate(nums[1:-1], start=1):
        for (rowidx, value) in enumerate(col[1:-1], start=1):
            if max(col[:rowidx]) < value:
                continue
            if max(col[rowidx+1:]) < value:
                continue
            inverted = [x[rowidx] for x in nums]
            if max(inverted[:colidx]) < value:
                continue
            if max(inverted[colidx+1:]) < value:
                continue
            yield ((colidx, rowidx), value)

if __name__ == '__main__':
    with open('input.txt') as fptr:
        nums: list[list[int]] = parse_text(fptr.read())
    invisible_trees = list(not_visible_2d(nums))
    print(f"invisible trees: {len(invisible_trees)}")
    total_trees = len(nums) * len(nums[0])
    visible_trees = total_trees - len(invisible_trees)
    print(f"visible trees: {visible_trees}")
