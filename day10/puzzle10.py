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
                yield (f"addx2 {value}", state_x)
                state_x += value

def render_screen(instructions: Iterable[Instruction]) -> list[str]:
    """renders a screen using the instructions passed in"""
    @dataclass
    class SpritePos:
        pc: int
        def is_pixel_lit(self, x_val: int) -> bool:
            return (self.pc % 40) in (x_val-1, x_val, x_val+1)
    machine_iter: Iterator[int] = (x for (_, x) in execute(instructions))
    sprites = [SpritePos(x) for x in range(240)]
    on_iter = (sp.is_pixel_lit(p) for (sp, p) in zip(sprites, machine_iter))
    pixels = ''.join("#" if on else "." for on in on_iter)
    screen = [
        pixels[0:40],
        pixels[40:80],
        pixels[80:120],
        pixels[120:160],
        pixels[160:200],
        pixels[200:240]
    ]
    return screen

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file to read")
    matches = parser.parse_args()
    with open(matches.input) as fptr:
        instructions = list(decode_instructions(fptr))
        machine_iter = list(enumerate(execute(instructions), start=1))
        cycles = {20, 60, 100, 140, 180, 220}
        stronks_of_interest = [(pc, x) for (pc, (_, x)) in machine_iter if pc in cycles]
        print(f"strengths: {stronks_of_interest}")
        total_stronk = sum(pc * x for (pc, x) in stronks_of_interest)
        print(f"sum: {total_stronk}")
        for line in render_screen(instructions):
            print(line)