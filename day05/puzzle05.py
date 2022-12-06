"""https://adventofcode.com/2022/day/5"""
import copy
from dataclasses import dataclass
from enum import Enum
import itertools
import re
from typing import Iterator, Tuple

_MOVE_RE = re.compile(r"^move\s+(?P<move>\d+)\s+from\s+(?P<from>\d+)\s+to\s+(?P<to>\d+)")

def parse_stack_lines(lines: list[str]) -> list[list[str]]:
    """
    parses the lines from the input into a list of stacks

    > parse_stack_lines(["    [D]", "[N] [C]", "[Z] [M] [P]", "1   2   3"])
    [["N", "Z"], ["D", "C", "M"], ["P"]]
    """
    column_idxs: list[int] = [m.start() for m in re.finditer(r"\d+", lines[-1])]
    stacks = [list() for _ in range(len(column_idxs))]
    for each_line in lines[:-1]:
        for (stack_idx, each_column_idx) in enumerate(column_idxs):
            if each_column_idx < len(each_line) and each_line[each_column_idx] != ' ':
                stacks[stack_idx].append(each_line[each_column_idx])
    return stacks

@dataclass
class Move:
    """describes a move of a stack"""
    num: int
    source: int
    dest: int
    @classmethod
    def parse(cls, text: str)-> 'Move':
        """
        parses text into a dataclass (note source/dest are converted to 0-based indexing)

        > Move.parse("move 3 from 1 to 3")
        Move(num=3, source=0, dest=2)
        """
        if m := _MOVE_RE.match(text):
            return Move(num=int(m.group("move")),
                        source=int(m.group("from")) - 1,
                        dest=int(m.group("to")) - 1)
        raise ValueError(f"failed to parse text to Move: {text}")
        

def parse_move_lines(lines: list[str]) -> list[Move]:
    """parses the move lines into moves"""
    return [Move.parse(t) for t in lines]

def parse_lines(lines: list[str]) -> Tuple[list[list[str]], list[Move]]:
    """parses text lines into two lists containing the stacks, and the moves"""
    it = iter(lines)
    # split the text on the empty line between the stacks and the moves
    stacks_text = list(itertools.takewhile(lambda s: s.strip(), it))
    moves_text = list(it)
    stacks = parse_stack_lines(stacks_text)
    moves = parse_move_lines(moves_text)
    return (stacks, moves)

class InsertOrder(Enum):
    """Defines an Insertion Order"""
    Maintained = 0,
    Reversed = 1
    @property
    def is_reversed(self) -> bool:
        return self == self.Reversed

def perform_move(move: Move, stacks: list[list[str]], *, order=InsertOrder.Reversed):
    """performs a Move in-place on stacks"""
    def pop_n(num: int, seq: list, reversed=False):
        """pops num elements from start of list"""
        acc = []
        fn = acc.append if reversed else lambda elem: acc.insert(0, elem)
        [fn(seq.pop(0)) for _ in range(num)]
        return acc
    items = pop_n(move.num, stacks[move.source], reversed=order.is_reversed)
    [stacks[move.dest].insert(0, i) for i in items] # annoying, list.insert only takes 1 element at a time
    return stacks

if __name__ == '__main__':
    with open('input.txt') as fptr:
        lines = fptr.read().splitlines()
    (stacks, moves) = parse_lines(lines)
    stacks_p1 = copy.deepcopy(stacks)
    for each_move in moves:
        perform_move(each_move, stacks_p1)
    top_p1 = ''.join(s[0] for s in stacks_p1)
    print(f"tops of stack (part 1): {top_p1}")
    for each_move in moves:
        perform_move(each_move, stacks, order=InsertOrder.Maintained)
    top_p2 = ''.join(s[0] for s in stacks)
    print(f"tops of stack (part 2): {top_p2}")