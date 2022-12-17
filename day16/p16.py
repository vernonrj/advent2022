"""https://adventofcode.com/2022/day/16"""

import argparse
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from functools import reduce
import re
from typing import Iterable, Iterator, Self


INPUT_RE = re.compile(r"Valve (?P<valve>[A-Z]+) has flow rate=(?P<rate>\d+); tunnel(s?) lead(s?) to valve(s?) (?P<connected>([A-Z]+(, )?)+)")

@dataclass(frozen=True)
class Valve:
    ident: str
    rate: int
    connected: frozenset[str]

ValveDict = dict[str, Valve]

def parse_input(text: Iterable[str]) -> Iterator[Valve]:
    """parses the input text"""
    for line in text:
        if m := INPUT_RE.match(line):
            valve = m.group("valve")
            rate = int(m.group("rate"))
            connected = frozenset(m.group("connected").split(', '))
            yield Valve(ident=valve, rate=rate, connected=connected)
        else:
            raise ValueError(f"failed to parse line `{line}`")

def connections(valves: ValveDict, this_valve: Valve) -> Iterator[Valve]:
    """Returns an iterator of all valves that this one is connected to"""
    for conn in this_valve.connected:
        yield valves[conn]

@dataclass(frozen=True)
class TraverseOperation:
    destination: Valve

@dataclass(frozen=True)
class OpenValveOperation:
    valve: Valve

Operation = TraverseOperation | OpenValveOperation

@dataclass(frozen=True)
class TreeNode:
    """oh shit oh fuck it's a tree. we're really getting CS-y now"""
    node: Valve
    parents: list[Operation]
    valves: ValveDict
    enabled: set[Valve]
    def __post_init__(self):
        assert isinstance(self.node, Valve)
        assert isinstance(self.valves, dict)
    @property
    def elapsed(self) -> int:
        """returns the time elapsed for this node"""
        return len(self.parents) # lol, each operation takes a minute :)
    @property
    def flow_rate(self) -> int:
        """returns the current flow rate"""
        return sum(v.rate for v in self.enabled)
    def traverse(self, child: Valve) -> Self:
        """make a Traversal node to `child`"""
        assert child.ident in self.node.connected, f"child {child} must be included in this node's tunnels ({self.node.connected})"
        newnode = TreeNode(
            node=child,
            parents = self.parents + [TraverseOperation(destination=child)],
            valves=self.valves,
            enabled=set(self.enabled),
        )
        return newnode
    def open_valve(self) -> Self:
        """return an OpenValvue node"""
        if self.node in self.enabled:
            raise ValueError("attempt to open valve that has already been opened")
        newnode = TreeNode(
            node=self.node,
            parents = self.parents + [OpenValveOperation(valve=self.node)],
            valves=self.valves,
            enabled=self.enabled | {self.node},
        )
        return newnode
    def children(self) -> list[Self]:
        """returns all children that stay under the 30 minute time limit"""
        # there are two operations we can do: turn the valve here, or move to another node.
        # turning the valve can only be done once, but we can traverse to our hearts' content,
        # so long as we stay below 30 minutes
        child_valves: Iterator[Valve] = (self.valves[vid] for vid in self.node.connected)
        kinder: list[Self] = [self.traverse(child) for child in child_valves]
        # we should check to see if the valve for this node has been turned on this path yet
        # Also if the flow rate is zero, we shouldn't bother opening it
        if self.node not in self.enabled and self.node.rate > 0:
            # TODO: for now, we ALWAYS require unopened useful valves to be opened to reduce complexity
            # kinder.append(self.open_valve())
            kinder = [self.open_valve()]
        # filter out all paths that are too long
        kinder = [k for k in kinder if k.elapsed <= 30]
        return kinder

def find_path(valves: ValveDict, start: Valve, goal: Valve) -> list[Valve]:
    """find the minimum path between `source` and `dest`, using A*"""
    def reconstruct_path(came_from: dict[Valve, Valve], current: Valve) -> list[Valve]:
        """uses `came_from` to build a path from a start point to `current`"""
        total_path = [current]
        while preceding := came_from.get(current):
            total_path.insert(0, preceding)
            current = preceding
        return total_path

    open_set = [start]
    came_from: dict[Valve, Valve] = {}

    # cheapest path from start to `node`
    g_score: dict[Valve, float] = defaultdict(lambda: float('inf'))
    g_score[start] = 0.0
    # f_score[node] = g_score[node] + h(node).
    # best guess for how cheap a path could be from start to finish if it traverses `node`
    # f_score: dict[Valve, float] = defaultdict(lambda: float('inf'))
    # f_score[start] = grid.h(start)
    while open_set:
        # open_set.sort(key=lambda p: f_score.get(p, float('inf')))
        current = open_set.pop(0)
        if current == goal:
            return reconstruct_path(came_from, current)
        for each_neighbor in [valves[v] for v in current.connected]:
            tentative_gscore = g_score[current] + 1
            if tentative_gscore < g_score[each_neighbor]:
                # this path to neighbor is better than any previous one. Record it!
                came_from[each_neighbor] = current
                g_score[each_neighbor] = tentative_gscore
                # f_score[each_neighbor] = tentative_gscore + grid.h(each_neighbor)
                if each_neighbor not in open_set:
                    open_set.append(each_neighbor)
    raise ValueError("open_set is empty but goal was never reached!")

def build_path(valve_trav: list[Valve], valves: ValveDict) -> list[TreeNode]:
    """build a traversal graph vising `valves` in order"""
    start: Valve = valve_trav.pop(0)
    assert isinstance(start, Valve)
    path: list[TreeNode] = [TreeNode(
        node=start,
        parents=[],
        valves=valves,
        enabled=set(),
    )]
    for each in valve_trav:
        to_next_node: list[TreeNode] = find_path(valves, start, each)
        for each_node in to_next_node[1:]:
            assert isinstance(each_node, Valve)
            path.append(path[-1].traverse(each_node))
        path.append(path[-1].open_valve())
        start = each
    return path

def solve1(valves: ValveDict) -> list[TreeNode]:
    """return the max flow rate you can achieve with valves"""
    path: list[TreeNode] = [TreeNode(
        node=valves["AA"],
        parents=[],
        valves=valves,
        enabled=set(),
    )]
    def cost_function(source: Valve, dest: Valve):
        between_source_dest = find_path(valves, source, dest)
        return (30 - len(path)) * dest.rate / len(between_source_dest)
    valve_weights = sorted(valves.values(), key=lambda v: cost_function(valves["AA"], v), reverse=True)
    while valve_weights:
        valve = valve_weights.pop(0)
        valve_weights = sorted(valve_weights, key=lambda v: cost_function(valve, v), reverse=True)
        print(f"best valves: {list(v.ident for v in valve_weights)}")
        if len(path) == 30:
            return path
        to_next_node = find_path(valves, path[-1].node, valve)
        for each_node in to_next_node[1:]:
            path.append(path[-1].traverse(each_node))
        path.append(path[-1].open_valve())
    return path

def swapper(seq) -> Iterator[list]:
    """fuck I dunno what I'm doing"""
    for idx in range(1, len(seq)):
        newseq = [*seq[:idx-1], seq[idx], seq[idx-1], *seq[idx+1:]]
        yield newseq

def pressure(path: list[TreeNode]) -> int:
    """calculates the total pressure for a path"""
    total = 0
    pressure_until_now = set()
    for (idx, operation) in enumerate(path[-1].parents):
        match operation:
            case TraverseOperation(destination):
                # print(f"minute {idx+1}: traverse to {destination.ident}")
                pass
            case OpenValveOperation(valve):
                pressure_until_now |= {valve}
                print(f"minute {idx+1}: open valve {valve.ident} with flow rate {valve.rate}, releasing {sum(v.rate for v in pressure_until_now)} total")
                total += valve.rate * (29 - idx)
    return total

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file")
    matches = parser.parse_args()
    with open(matches.input) as fptr:
        valves: list[Valve] = list(parse_input(fptr.read().splitlines()))
        valve_dict = {v.ident: v for v in valves}
        path = solve1(valve_dict)
        open_valves = [n.valve for n in path[-1].parents if isinstance(n, OpenValveOperation)]
        print(f"open: {[v.ident for v in open_valves]}, pressure: {sum(v.rate for v in open_valves)}")
        best_pressure = pressure(path[:30])
        # for alt in swapper(open_valves):
        #     print(f"try alt {[v.ident for v in alt]}")
        #     path = build_path([valve_dict['AA']] + alt, valve_dict)
        #     new_pressure = pressure(path[:30])
        #     if new_pressure > best_pressure:
        #         print(f"found better pressure: {new_pressure}")
        #         best_pressure = new_pressure
        print(best_pressure)