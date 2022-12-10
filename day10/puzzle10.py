"""https://adventofcode.com/2022/day/10"""

import argparse
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Iterator, Tuple

class InstructionTag(Enum):
    NoOp = "noop"
    Addx = "addx"

@dataclass
class NoOp:
    pass

@dataclass
class Addx:
    value: int
    def __post_init__(self):
        self.value = int(self.value)

Instruction = Addx | NoOp

def decode_instructions(lines: Iterable[str]) -> Iterator[Instruction]:
    """decode lines into instructions"""
    for line in lines:
        (inst_str, *args) = line.split()
        match InstructionTag(inst_str):
            case InstructionTag.NoOp:
                yield NoOp(*args)
            case InstructionTag.Addx:
                yield Addx(*args)
            case err:
                raise ValueError(f"failed to decode instruction {err}")

def execute(instructions: Iterable[Instruction]) -> Iterator[Tuple[str, int]]:
    """ooh fancy generator time!"""
    state_x = 1
    for each in instructions:
        match each:
            case NoOp():
                yield ("noop", state_x)
            case Addx(value):
                yield (f"addx1 {value}", state_x)
                state_x += value
                yield (f"addx2 {value}", state_x)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file to read")
    matches = parser.parse_args()
    with open(matches.input) as fptr:
        instructions = list(decode_instructions(fptr))
        machine_iter = list(enumerate(execute(instructions), start=1))
        # for line in machine_iter[:220]:
        #     print(line)
        cycles = {19, 59, 99, 139, 179, 219} # we want DURING, not AFTER the 20/60/100/etc cycle, so check the end of the PREVIOUS cycle.
        stronks_of_interest = [(pc+1, x) for (pc, (_, x)) in machine_iter if pc in cycles]
        print(f"strengths: {stronks_of_interest}")
        total_stronk = sum(pc * x for (pc, x) in stronks_of_interest)
        print(f"sum: {total_stronk}")