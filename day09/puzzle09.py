"""https://adventofcode.com/2022/day/9"""

# Head and Tail are the head and tail of a rope. The head is moved, and the tail follows, like so:
# There are 8 possible initial tail positions
#
#   TTT
#   THT
#   TTT
#
# here are the possible locations of H after a single move
#  
#   THT
#   H H 
#   THT
#
# T can thus be in any of these positions in relation to H (including overlapped)
# the second image shows positions of T where a move must occur (and the direction):
#                 
#      TTT          \|/   
#     TTTTT        \TTT/  
#     TTHTT        -THT-
#     TTTTT        /TTT\  
#      TTT          /|\   
#                 
# (note: part 2 has more possible positions, but is the same idea)

from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
import logging
from typing import Iterable, Iterator, Tuple

def parse_movelist(lines: list[str]) -> Iterator[Tuple['Move', int]]:
    """parses a list of lines into a list of moves"""
    for line in lines:
        match line.split():
            case ["U", y]:
                yield (Move.Up, int(y))
            case ["D", y]:
                yield (Move.Down, int(y))
            case ["L", x]:
                yield (Move.Left, int(x))
            case ["R", x]:
                yield (Move.Right, int(x))
            case err:
                raise ValueError(f"failed to parse input {err}")

@dataclass(eq=True, frozen=True)
class Point:
    x: int
    y: int
    def __add__(self, other: 'Point') -> 'Point':
        return Point(self.x + other.x, self.y + other.y)
    def __sub__(self, other: 'Point') -> 'Point':
        return Point(self.x - other.x, self.y - other.y)

def simulate_moves(movelist: Iterable[Tuple['Move', int]], rope_length: int) -> set[Point]:
    """simulates the moves from a movelist for a rope of length `rope_length`, returning the points visited"""
    rope = [Point(0, 0) for _ in range(rope_length)]
    visited: set[Point] = {rope[-1]}
    for (move, times) in movelist:
        rope = move.apply(rope, times=times, visited=visited)
        visited.add(rope[-1])
    return visited

class Move(Enum):
    Up = (0, 1)
    Down = (0, -1)
    Left = (-1, 0)
    Right = (1, 0)
    def apply(self, rope: list[Point], *, times: int = 1, visited: set[Point] = None) -> list[Point]:
        """apply a movement to the head and tail, returning (head, tail)"""
        (x, y) = self.value
        # print(f"\n{self} {times} times")
        for _ in range(times):
            (head, *rest) = rope
            head = Point(x=head.x + x, y=head.y+y)
            new_rope = [head]
            for tail in rest:
                tail = move_tail(head=head, tail=tail)
                new_rope.append(tail)
                head = tail
            rope = new_rope
            # print_field(rope)
            if visited is not None:
                visited.add(tail)
        return rope

def move_tail(*, head: Point, tail: Point) -> Point:
    """move the tail to a new point"""
    logger = logging.getLogger()
    logger.info("move tail to follow head: (head, tail) = (%s, %s)", head, tail)
    match head - tail:
        case Point(x, y) if abs(x) <= 1 and abs(y) <= 1:
            logger.info("no movement")
            return tail
        case Point(x, y) if abs(y) == abs(x):
            logger.info("x and y distance of 2")
            new_x = (head.x - 1) if x > 0 else (head.x + 1)
            new_y = (head.y - 1) if y > 0 else (head.y + 1)
            return Point(new_x, new_y)
        case Point(x, y) if abs(y) > abs(x):
            logger.info("y distance of 2")
            new_y = (head.y - 1) if y > 0 else (head.y + 1)
            return Point(head.x, new_y)
        case Point(x, y) if abs(x) > abs(y):
            logger.info("x distance of 2")
            new_x = (head.x - 1) if x > 0 else (head.x + 1)
            return Point(new_x, head.y)
        case _ as err:
            raise ValueError(f"invalid tail position. Head: {head}, Tail: {tail}. (Head - Tail = {err})")

def print_field(rope: list[Point]):
    """prints the field"""
    max_x = max(r.x for r in (rope + [Point(0, 0)]))
    min_x = min(r.x for r in (rope + [Point(0, 0)]))
    max_y = max(r.y for r in (rope + [Point(0, 0)]))
    min_y = min(r.y for r in (rope + [Point(0, 0)]))
    field = [["." for _ in range(min_x, max_x+1)] for _ in range(min_y, max_y+1)]
    [head, *rest] = rope
    field[-min_y][-min_x] = "s"
    field[head.y - min_y][head.x - min_x] = "H"
    for (idx, tail) in enumerate(reversed(rest), start=1):
        token = str(len(rope) - idx) if len(rest) != 1 else "T"
        field[tail.y - min_y][tail.x - min_x] = token
    for row in reversed(field):
        print(''.join(row))
    print()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('input', help='input file')
    matches = parser.parse_args()
    with open(matches.input) as fptr:
        moves = list(parse_movelist(fptr))
        visited_r2 = simulate_moves(moves, rope_length=2)
        print(f"visited (rope length=2) = {len(visited_r2)}")
        visited_r10 = simulate_moves(moves, rope_length=10)
        print(f"visited (rope length=10 = {len(visited_r10)}")