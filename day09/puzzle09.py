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

from argparse import ArgumentParser
from dataclasses import dataclass
import copy
from enum import Enum
import logging
from typing import Iterator, Tuple

class Move(Enum):
    Up = (0, 1)
    Down = (0, -1)
    Left = (-1, 0)
    Right = (1, 0)
    def apply(self, *, head: 'Point', tail: 'Point', times: int = 1, visited: set['Point'] = None) -> Tuple['Point', 'Point']:
        """apply a movement to the head and tail, returning (head, tail)"""
        (x, y) = self.value
        for _ in range(times):
            head = Point(x=head.x + x, y=head.y+y)
            tail = move_tail(head=head, tail=tail)
            if visited is not None:
                visited.add(tail)
        return (head, tail)

def parse_movelist(lines: list[str]) -> Iterator[Tuple[Move, int]]:
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

def move_tail(*, head: Point, tail: Point) -> Point:
    """calculation to move the tail to a new point"""
    logger = logging.getLogger()
    logger.info("move tail to follow head: (head, tail) = (%s, %s)", head, tail)
    match head - tail:
        case Point(x, y) if abs(x) <= 1 and abs(y) <= 1:
            logger.info("no movement")
            return tail
        case Point(x, 2) | Point(x, -2) as p:
            logger.info("y distance of 2")
            assert x in (-1, 0, 1)
            new_y = (tail.y + 1) if p.y > 0 else (tail.y - 1)
            return Point(head.x, new_y)
        case Point(2, y) | Point(-2, y) as p:
            logger.info("x distance of 2")
            assert y in (-1, 0, 1)
            new_x = (tail.x + 1) if p.x > 0 else (tail.x - 1)
            return Point(new_x, head.y)
        case _ as err:
            raise ValueError(f"invalid tail position. Head: {head}, Tail: {tail}. (Head - Tail = {err})")

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('input', help='input file')
    matches = parser.parse_args()
    head = Point(x=0, y=0)
    tail = Point(x=0, y=0)
    visited: set[Point] = {copy.copy(tail)}
    with open(matches.input) as fptr:
        moves = parse_movelist(fptr)
        for (move, times) in moves:
            (head, tail) = move.apply(head=head, tail=tail, times=times, visited=visited)
            visited.add(copy.copy(tail))
    print(f"head = {head}, tail = {tail}, visited = {len(visited)}")

