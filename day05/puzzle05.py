"""https://adventofcode.com/2022/day/5"""
from dataclasses import dataclass
import itertools
import re
from typing import Iterator, Tuple

_MOVE_RE = re.compile(r"^move\s+(?P<move>\d+)\s+from\s+(?P<from>\d+)\s+to\s+(?P<to>\d+)")

def parse_stack_lines(lines: list[str]) -> list[list[str]]:
    """
    parses the lines from the input into a list of stacks

    parse_stack_lines(["    [D]", "[N] [C]", "[Z] [M] [P]", "1   2   3"])
    [["N", "Z"], ["D", "C", "M"], ["P"]]
    """
    columns: list[int] = [m.start() for m in re.finditer(r"\d+", lines[-1])]
    stacks = [list() for _ in range(len(columns))]
    for each_line in lines[:-1]:
        for (idx, each_column) in enumerate(columns):
            if each_column < len(each_line) and each_line[each_column] != ' ':
                stacks[idx].append(each_line[each_column])
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

def perform_move(move: Move, stacks: list[list[str]]):
    """performs a Move in-place on stacks"""
    def pop_n(num: int, seq: list):
        """pops num elements from start of list. doesn't fail if len(list) < n, just returns len(list) instead"""
        acc = []
        for _ in range(num):
            try:
                acc.append(seq.pop(0))
            except IndexError:
                pass
        return acc
    items = pop_n(move.num, stacks[move.source])
    [stacks[move.dest].insert(0, i) for i in items] # annoying, list.insert only takes 1 element at a time
    return stacks

if __name__ == '__main__':
    with open('input.txt') as fptr:
        lines = fptr.read().splitlines()
    (stacks, moves) = parse_lines(lines)
    for each_move in moves:
        perform_move(each_move, stacks)
    top = ''.join(s[0] for s in stacks)
    print(f"tops of stack: {top}")