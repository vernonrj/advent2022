"""https://adventofcode.com/2022/day/14"""

import argparse
from dataclasses import dataclass
from enum import Enum
import itertools
from typing import Iterator, Optional, Self, Tuple

@dataclass
class Point:
    x: int
    y: int
    @classmethod
    def parse(cls, text: str) -> Self:
        """parses text such as `498,4` into a Point class"""
        x, y = text.strip().split(',')
        return cls(x=int(x), y=int(y))
    @classmethod
    def line(cls, start: Self, end: Self) -> list[Self]:
        """creates a line of `Point`s from start to end"""
        if start.x == end.x:
            (ystart, yend) = sorted([start.y, end.y])
            return [Point(start.x, y) for y in range(ystart, yend+1)]
        if start.y == end.y:
            (xstart, xend) = sorted([start.x, end.x])
            return [Point(x, start.y) for x in range(xstart, xend+1)]
        raise ValueError(f"cannot construct line from {start} to {end}: only straight lines supported")

class GridElem(Enum):
    Empty = '.'
    Rock = '#'
    Sand = 'o'
    def is_empty(self) -> bool:
        return self == self.Empty

class Grid:
    def __init__(self):
        self.grid = [[]]
        self.minx = 0xffffffff
        self.miny = 0xffffffff
        self.floor_y = None
    def _make_floor(self):
        """normalizes the unbounded floor at our new dimensions"""
        if not self.floor_y:
            self.floor_y = len(self.grid) + 2
        if self.floor_y >= len(self.grid):
            self._extend_y(self.floor_y)
        self.grid[self.floor_y-1] = [GridElem.Rock] * len(self.grid[-1])
    def _extend_y(self, new_ymax: int):
        """extends the grid Y-axis dimension"""
        extend_by = new_ymax - len(self.grid) + 1
        for _ in range(extend_by):
            self.grid.append([GridElem.Empty] * len(self.grid[0]))
    def _extend_x(self, new_xmax: int):
        """extends the grid X-axis dimension"""
        extend_by = new_xmax - len(self.grid[0]) + 1
        for row in self.grid:
            row.extend([GridElem.Empty] * extend_by)
        if self.floor_y:
            self._make_floor()
    def insert(self, coord: Point, elem: GridElem):
        """inserts an element into the grid"""
        self.minx = min(self.minx, coord.x)
        self.miny = min(self.miny, coord.y)
        if coord.y >= len(self.grid):
            self._extend_y(coord.y)
        if coord.x >= len(self.grid[0]):
            self._extend_x(coord.x)
        self.grid[coord.y][coord.x] = elem
    def value(self, coord: Point) -> GridElem:
        """returns value at coord"""
        if coord.y >= len(self.grid):
            if not self.floor_y:
                return GridElem.Empty # special case: we're in the endless void
            self._make_floor()
        try:
            return self.grid[coord.y][coord.x]
        except IndexError:
            if self.floor_y:
                # extend the grid to cover this
                self._extend_x(max(coord.x, len(self.grid[-1])) + 20)
                return self.grid[coord.y][coord.x]
            # we don't care about this IndexError though
            return GridElem.Empty
    def fell_into_the_void(self, coord: Point) -> bool:
        """returns True if the sand is below the level of rock"""
        return coord.y >= len(self.grid)

def parse_lines(text: Iterator[str]) -> Grid:
    """parses the text into a grid"""
    grid = Grid()
    for textline in text:
        points = [Point.parse(p) for p in textline.split('->')]
        point_pairs = itertools.pairwise(points)
        for (start, end) in point_pairs:
            pointline = Point.line(start, end)
            for each in pointline:
                grid.insert(each, GridElem.Rock)
    return grid

class EndlessVoidIndexError(IndexError):
    """marks the endless void below the lowest rock"""

class SandFellIntoTheEndlessVoidError(Exception):
    """marks when the sand fell off into the endless void"""

class EmitSandError(Exception):
    """cannot emit sand from the hole"""

def drop_sand(grid: Grid) -> Point:
    """drop a piece of sand, returning where it ends. raises SandFellIntoTheEndlessVoid if sand falls into the endless void"""
    sand = Point(500, 0)
    if grid.value(sand) == GridElem.Sand:
        raise EmitSandError("cannot emit a grain of sand")
    while True:
        if grid.fell_into_the_void(sand):
            raise SandFellIntoTheEndlessVoidError(f"point {sand} belongs to the void")
        below = Point(sand.x, sand.y+1)
        downleft = Point(sand.x-1, sand.y+1)
        downright = Point(sand.x+1, sand.y+1)
        if grid.value(below).is_empty():
            sand = below # sand can fall down. we continue letting the sand fall
            continue
        if grid.value(downleft).is_empty():
            sand = downleft # sand can fall down and to the left. we continue letting the sand fall
            continue
        if grid.value(downright).is_empty():
            sand = downright # sand can fall down and to the right. we continue letting the sand fall
            continue
        # sand can't go down anymore. it has settled.
        grid.insert(sand, GridElem.Sand)
        break

def solve(grid: Grid, max_iterations: int = 1000):
    for row in grid.grid:
        print(''.join(x.value for x in row[grid.minx:]))
    print()
    try:
        for times in range(1, max_iterations+1):
            drop_sand(grid)
    except SandFellIntoTheEndlessVoidError:
        # rad, it worked!
        print(f"{times-1} grains of sand fell into the void")
    except EmitSandError:
        # it worked even better!
        print(f"{times-1} grains of sand fell until the top was clogged")
    else:
        raise AssertionError("dropped a bunch of sand and none of it fell into the void :( the void hungers :(")
    for row in grid.grid:
        print(''.join(x.value for x in row[grid.minx:]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="file to read from")
    matches = parser.parse_args()
    with open(matches.input) as fptr:
        lines = fptr.read().splitlines()
    grid = parse_lines(lines)
    solve(grid)
    grid = parse_lines(lines)
    grid._make_floor()
    solve(grid, max_iterations=100000)