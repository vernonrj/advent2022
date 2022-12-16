"""https://adventofcode.com/2022/day/15"""

import argparse
from dataclasses import dataclass
import itertools
import re
from typing import Callable, Iterable, Iterator, Self

INPUT_RE = re.compile(r"Sensor at x=(?P<sx>[-0-9]+), y=(?P<sy>[-0-9]+): closest beacon is at x=(?P<bx>[-0-9]+), y=(?P<by>[-0-9]+)")

@dataclass(frozen=True)
class Point:
    x: int
    y: int
    def __post_init__(self):
        assert isinstance(self.x, int)
        assert isinstance(self.y, int)
    def __add__(self, other: Self) -> Self:
        return Point(self.x + other.x, self.y + other.y)
    @classmethod
    def manhattan_distance(cls, p1: Self, p2: Self) -> int:
        """returns the manhattan distance between two points"""
        return abs(p2.y - p1.y) + abs(p2.x - p1.x)
    @classmethod
    def range_inclusive(cls, start: Self, end: Self) -> Iterator[Self]:
        if start.x == end.x:
            return (Point(start.x, y) for y in range(start.y, end.y+1))
        if start.y == end.y:
            return (Point(x, start.y) for x in range(start.x, end.x+1))
        raise ValueError(f"both xs or both ys must be equal")

@dataclass
class Sensor:
    location: Point
    closest_beacon: Point
    @classmethod
    def parse(cls, text: str) -> Self:
        """parses a line of input into a Sensor descriptor"""
        if m := INPUT_RE.match(text):
            return cls(
                location=Point(x=int(m.group("sx")), y=int(m.group("sy"))),
                closest_beacon=Point(x=int(m.group("bx")), y=int(m.group("by")))
            )
        raise ValueError(f"failed to parse text {text}")
    def closer_than_beacon(self, poi: Point) -> bool:
        """returns True if a point of interest is closer than this sensor's beacon"""
        beacon_dist: int = Point.manhattan_distance(self.location, self.closest_beacon)
        point_dist: int = Point.manhattan_distance(self.location, poi)
        return point_dist <= beacon_dist

def parse_input(lines: Iterable[str]) -> Iterator[Sensor]:
    """parses the input into an iterator of sensors"""
    return (Sensor.parse(s) for s in lines)

def point_covered_by(point: Point, sensors: list[Sensor]) -> Iterator[Sensor]:
    """return all sensors whose beacons are further away than `point` i.e. whether their beacons "cover" this point"""
    return (s for s in sensors if s.closer_than_beacon(point))

def apply_x(sensors: list[Sensor], func: Callable[[list[Point]], Point]) -> int:
    """returns the x value using key function for a list of sensors"""
    points = (func(s.location, s.closest_beacon, key=lambda p: p.x) for s in sensors)
    applied_point = func(points, key=lambda p: p.x)
    return applied_point.x

def around(point: Point, distance: int) -> Iterator[Point]:
    """returns an iterator of points `distance` away from `point`"""
    for x in range(0, distance+1):
        y = distance - x
        yield point + Point(x, y)
        if y:
            yield point + Point(x, -y)
        if x:
            yield point + Point(-x, y)
        if x and y:
            yield point + Point(-x, -y)

def solve1(sensors: list[Sensor], y_val: int = 2000000):
    """finds all points covered by beacons at a specific y-value"""
    max_dist = max(Point.manhattan_distance(s.location, s.closest_beacon) for s in sensors)
    min_x = apply_x(sensors, min) - max_dist
    max_x = apply_x(sensors, max) + max_dist
    print(f"min/max = {min_x}, {max_x}")
    prange = list(Point.range_inclusive(Point(min_x, y_val), Point(max_x, y_val)))
    beacons = set(prange) & {s.closest_beacon for s in sensors}
    coverage = [(p, list(point_covered_by(p, sensors))) for p in prange]
    covered_by_beacons = [p for (p, cov) in coverage if cov and p not in beacons]
    # print(f"covered({len(covered_by_beacons)}): {covered_by_beacons}")
    c = len(covered_by_beacons)
    print(f"covered by beacons: {c}")

def solve2(sensors: list[Sensor], dim: int = 20):
    """finds the only point not covered by a beacon in an area of [0, dim] by [0, dim]"""
    for each in sensors:
        print(f"sensor: {each}")
        beacon_distance = Point.manhattan_distance(each.location, each.closest_beacon)
        for point in around(each.location, beacon_distance + 1):
            if point.x < 0 or point.x > dim or point.y < 0 or point.y > dim:
                # point is outside the dimensions we're searching
                continue
            cov = point_covered_by(point, sensors)
            try:
                # we only need to check if this point is covered by _1 or more_ sensors,
                # and it's theoretically cheaper to not find all sensors this point is covered by,
                # so just try to get the first sensor/beacon that covers this point
                next(cov)
            except StopIteration:
                # no sensor/beacons cover this point. we've found it!
                print(f"found uncovered point at {point}")
                tuning_freq = point.x * 4000000 + point.y
                print(f"tuning frequency: {tuning_freq}")
                return
    raise ValueError("no point found")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file")
    matches = parser.parse_args()
    with open(matches.input) as fptr:
        sensors = list(parse_input(fptr.read().splitlines()))
        solve1(sensors)
        solve2(sensors, dim=4000000)
