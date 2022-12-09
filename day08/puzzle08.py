"""https://adventofcode.com/2022/day/8"""
import itertools
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

def scenic_scores(nums: list[list[int]]) -> Tuple[int, int, int]:
    """returns the "scenic score" of a tee"""
    for (colidx, col) in enumerate(nums[1:-1], start=1):
        for (rowidx, value) in enumerate(col[1:-1], start=1):
            def trees_seen(tree_candidates: list[int]) -> int:
                if not tree_candidates:
                    return 0
                shorter_trees = list(itertools.takewhile(lambda x: x < value, tree_candidates))
                trees_seen = len(shorter_trees)
                if shorter_trees != tree_candidates:
                    trees_seen += 1 # we also see the taller tree
                return trees_seen
            left_score = trees_seen(list(reversed(col[:rowidx])))
            right_score = trees_seen(col[rowidx+1:])
            inverted = [x[rowidx] for x in nums]
            up_score = trees_seen(list(reversed(inverted[:colidx])))
            down_score = trees_seen(inverted[colidx+1:])
            yield left_score * right_score * up_score * down_score

if __name__ == '__main__':
    with open('input.txt') as fptr:
        nums: list[list[int]] = parse_text(fptr.read())
    invisible_trees = list(not_visible_2d(nums))
    print(f"invisible trees: {len(invisible_trees)}")
    total_trees = len(nums) * len(nums[0])
    visible_trees = total_trees - len(invisible_trees)
    print(f"visible trees: {visible_trees}")
    max_scenic = max(scenic_scores(nums))
    print(f"best scenic score = {max_scenic}")
