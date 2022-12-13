"""https://adventofcode.com/2022/day/12"""
import argparse
from collections import defaultdict
from dataclasses import dataclass
import io
import math
from typing import Callable, Iterator, Tuple

class NoSolutionError(ValueError):
    """raises if there is no solution to (start, end)"""

@dataclass(frozen=True)
class Point:
    x: int
    y: int
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

def parse_levels(text: list[str]) -> Tuple[list[list[int]], Point, Point]:
    """parses the input text into a list of list of levels. returns the Start and End locations too"""
    levels: list[list[int]] = []
    start = None
    end = None
    for (y, line) in enumerate(text):
        levels.append([])
        for (x, ch) in enumerate(line):
            if ch == 'S':
                start = Point(x, y)
                ch = 'a'
            elif ch == 'E':
                end = Point(x, y)
                ch = 'z'
            elif ch == '\n':
                raise ValueError("newline detected in input")
            levels[-1].append(calc_weight(ch))
    assert start is not None, "no start found!"
    assert end is not None, "no end found!"
    return (levels, start, end)

def calc_weight(ch: str) -> int:
    """calculates the weight of a character"""
    return ord(ch) - ord('a')

class Grid:
    """defines a grid with weights"""
    def __init__(self, weights: list[list[int]], *, start: Point, end: Point):
        self.start = start
        self.end = end
        self.weights = weights
    def find_all(self, pred: Callable[[Point], bool]) -> Iterator[Point]:
        """returns all nodes where pred(node) returns True"""
        for y in range(len(self.weights)):
            for x in range(len(self.weights[0])):
                p = Point(x, y)
                if pred(p):
                    yield p
    def neighbors(self, node: Point) -> Iterator[Point]:
        """returns a list of neighbors to `node`"""
        if node.x > 0:
            yield Point(node.x - 1, node.y)
        if node.y > 0:
            yield Point(node.x, node.y - 1)
        if node.x < len(self.weights[0]) - 1:
            yield Point(node.x + 1, node.y)
        if node.y < len(self.weights) - 1:
            yield Point(node.x, node.y + 1)
    def weight(self, node: Point) -> float:
        """returns the weight for a node"""
        return self.weights[node.y][node.x]
    def distance(self, start: Point, end: Point) -> int:
        """returns the distance function between two points"""
        start_weight = self.weight(start)
        stop_weight = self.weight(end)
        if stop_weight > (start_weight+1):
            return float('inf')
        return 1
    def h(self, node: Point) -> float:
        """returns the heuristic for a point"""
        return math.sqrt((node.y - self.end.y)**2 + (node.x - self.end.x)**2)

def a_star(start: Point, goal: Point, grid: Grid):
    """
    perform an A* search from start to goal

    straight implementation of the algorithm described on https://en.wikipedia.org/wiki/A*_search_algorithm
    """
    open_set = [start]
    came_from: dict[Point, Point] = {}

    # cheapest path from start to `node`
    g_score: dict[Point, float] = defaultdict(lambda: float('inf'))
    g_score[start] = 0.0
    # f_score[node] = g_score[node] + h(node).
    # best guess for how cheap a path could be from start to finish if it traverses `node`
    f_score: dict[Point, float] = defaultdict(lambda: float('inf'))
    f_score[start] = grid.h(start)
    while open_set:
        # TODO: can/should we use heapq for this?
        open_set.sort(key=lambda p: f_score.get(p, float('inf')))
        current = open_set.pop(0)
        if current == goal:
            return (reconstruct_path(came_from, current), came_from)
        for each_neighbor in grid.neighbors(current):
            tentative_gscore = g_score[current] + grid.distance(current, each_neighbor)
            if tentative_gscore < g_score[each_neighbor]:
                # this path to neighbor is better than any previous one. Record it!
                came_from[each_neighbor] = current
                g_score[each_neighbor] = tentative_gscore
                f_score[each_neighbor] = tentative_gscore + grid.h(each_neighbor)
                if each_neighbor not in open_set:
                    open_set.append(each_neighbor)
    raise NoSolutionError("open_set is empty but goal was never reached!")

def render_came_from(came_from: dict[Point, Point], good_path: list[Point], grid: Grid) -> str:
    """renders the dictionary describing predecessors"""
    buffer = io.StringIO()
    for y in range(len(grid.weights)):
        for x in range(len(grid.weights[0])):
            p = Point(x, y)
            if p == grid.start:
                buffer.write("S")
            if p == grid.end:
                buffer.write("E")
            direction_render = {
                Point(1, 0): '>',
                Point(-1, 0): '<',
                Point(0, 1): 'v',
                Point(0, -1): '^'
            }
            match [n for n in grid.neighbors(p) if came_from.get(n) == p]:
                case [n]:
                    buffer.write(direction_render[n - p])
                case [n, *rest]:
                    match set([n, *rest]) & set(good_path):
                        case [g]: buffer.write(direction_render[g - p])
                        case []: buffer.write(direction_render(n - p))
                        case [g, *bah]: buffer.write(direction_render(g - p))
                    # raise ValueError("too many neighbor options")
                case []:
                    buffer.write('.')
        buffer.write("\n")
    return buffer.getvalue()

def reconstruct_path(came_from: dict[Point, Point], current: Point) -> list[Point]:
    """uses `came_from` to build a path from a start point to `current`"""
    total_path = [current]
    while preceding := came_from.get(current):
        total_path.insert(0, preceding)
        current = preceding
    return total_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="file input")
    matches = parser.parse_args()
    with open(matches.input) as fptr:
        (weights, start, end) = parse_levels(fptr.read().splitlines())
    grid = Grid(weights, start=start, end=end)
    (path, came_from) = a_star(grid.start, grid.end, grid)
    print(f"part 1: finish in {len(path)-1} steps")
    # print(render_came_from(came_from, path, grid))
    all_lowest = grid.find_all(lambda p: grid.weight(p) == 0)
    shortest_path = len(path) - 1
    for each_start in all_lowest:
        grid.start = each_start
        # print(f"check start {each_start}")
        try:
            (path, _) = a_star(grid.start, grid.end, grid)
        except NoSolutionError:
            continue
        shortest_path = min(shortest_path, len(path) - 1)
    print(f"shortest path: {shortest_path}")