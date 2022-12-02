"""See https://adventofcode.com/2022/day/2"""

from abc import ABCMeta
from argparse import ArgumentParser
from enum import Enum

def add_score(object):
    def score(self) -> int:
        match self:
            case self.Rock:
                return 1
            case self.Paper:
                return 2
            case self.Scissors:
                return 3
            case _:
                raise ValueError(f"unsupported enum: {self}")
    object.score = score
    return object

@add_score
class EnemyMove(Enum):
    Rock = 'A'
    Paper = 'B'
    Scissors = 'C'

@add_score
class OurMove(Enum):
    Rock = 'X'
    Paper = 'Y'
    Scissors = 'Z'
    @classmethod
    def from_desired_outcome(cls, opponent: EnemyMove, desired: str):
        match (opponent, desired):
            case (EnemyMove.Paper, "X") | (EnemyMove.Rock, "Y") | (EnemyMove.Scissors, "Z"):
                return cls.Rock
            case (EnemyMove.Scissors, "X") | (EnemyMove.Paper, "Y") | (EnemyMove.Rock, "Z"):
                return cls.Paper
            case (EnemyMove.Rock, "X") | (EnemyMove.Scissors, "Y") | (EnemyMove.Paper, "Z"):
                return cls.Scissors
            case _:
                raise ValueError(f"unsupported combination: {opponent} with outcome {desired}")

class Outcome(Enum):
    Loss = 0
    Draw = 1
    Win = 2
    @classmethod
    def from_game(cls, opponent: EnemyMove, ours: OurMove):
        match (opponent, ours):
            case (EnemyMove.Rock, OurMove.Rock) | (EnemyMove.Paper, OurMove.Paper) | (EnemyMove.Scissors, OurMove.Scissors):
                # draw
                return Outcome.Draw
            case (EnemyMove.Rock, OurMove.Scissors) | (EnemyMove.Paper, OurMove.Rock) | (EnemyMove.Scissors, OurMove.Paper):
                # loss
                return Outcome.Loss
            case (EnemyMove.Rock, OurMove.Paper) | (EnemyMove.Paper, OurMove.Scissors) | (EnemyMove.Scissors, OurMove.Rock):
                # win
                return Outcome.Win
            case _:
                raise ValueError(f"unexpected input: {opponent} vs {ours}")
    def score(self) -> int:
        match self:
            case self.Loss:
                return 0
            case self.Win:
                return 6
            case self.Draw:
                return 3
            case _:
                raise ValueError(f"invalid outcome {self}")

def make_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("input", help="file to use as input")
    return parser

def decrypt_part1(rounds: list[str]) -> list[(EnemyMove, OurMove)]:
    """decrypts the rounds"""
    outcomes = []
    for line in rounds:
        (enemy_txt, our_txt) = line.strip().split(' ')
        enemy = EnemyMove(enemy_txt)
        ours = OurMove(our_txt)
        outcomes.append((enemy, ours))
    return outcomes

def decrypt_part2(rounds: list[str]) -> list[(EnemyMove, OurMove)]:
    """decrypt the rounds, but different"""
    games = []
    for line in rounds:
        (enemy_txt, our_txt) = line.strip().split(' ')
        enemy = EnemyMove(enemy_txt)
        ours = OurMove.from_desired_outcome(enemy, our_txt)
        games.append((enemy, ours))
    return games

def score_game(enemy: EnemyMove, ours: OurMove) -> int:
    """makes a score from the game"""
    outcome = Outcome.from_game(enemy, ours)
    return ours.score() + outcome.score()

if __name__ == '__main__':
    matches = make_parser().parse_args()
    with open(matches.input, 'r') as fptr:
        lines = fptr.readlines()
    games_1 = decrypt_part1(lines)
    print(sum(score_game(e, o) for (e, o) in games_1))
    games_2 = decrypt_part2(lines)
    print(sum(score_game(e, o) for (e, o) in games_2))