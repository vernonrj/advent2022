"""https://adventofcode.com/2022/day/11"""
import argparse
from dataclasses import dataclass
import operator
import re
from typing import Callable, Iterable, Iterator, Tuple

def parse_monkeys(text: Iterable[str]) -> Iterator['Monkey']:
    """Parses input text into monkeys"""
    current_monkey = {}
    divis_re = re.compile(r"divisible by (?P<mod>\d+)")
    throw_re = re.compile(r"throw to monkey (?P<m>\d+)")
    for line in text:
        if not line.strip():
            # finished parsing a monkey
            yield Monkey(**current_monkey)
            current_monkey.clear()
            continue
        if line.startswith("Monkey"):
            # we don't need the index, skip this line
            continue
        match line.strip().split(": "):
            case ["Starting items", items]:
                current_monkey['items'] = [int(x) for x in items.split(', ')]
            case ["Operation", oper]:
                current_monkey['operation'] = parse_operation(oper)
            case ["Test", test]:
                current_monkey['divisibility_test'] = int(divis_re.match(test).group("mod"))
            case ["If true", oper]:
                current_monkey['true_throw_to'] = int(throw_re.match(oper).group("m"))
            case ["If false", oper]:
                current_monkey['false_throw_to'] = int(throw_re.match(oper).group("m"))
            case err:
                raise ValueError(f"unexpected key: {err}")
    if current_monkey:
        yield Monkey(**current_monkey)

def parse_operation(text: str) -> Callable[[int], int]:
    """parses an operation into a callable"""
    oper_re = re.compile(r"new = old (?P<oper>\S+) (?P<num>\w+)")
    assert text.startswith("new = old "), f"operation MUST start with `new = old`, instead we got {text}"
    if m := oper_re.match(text):
        match m.group("oper"):
            case "+":
                oper = operator.add
            case "-":
                oper = operator.sub
            case "*":
                oper = operator.mul
            case "/":
                oper = operator.truediv
            case err:
                raise ValueError(f"unhandled symbol {err}")
        if m.group("num") == "old":
            return lambda old: oper(old, old)
        number = int(m.group("num"))
        return lambda old: oper(old, number)

@dataclass
class Monkey:
    items: list[int]
    operation: Callable[[int], int]
    divisibility_test: int
    true_throw_to: int
    false_throw_to: int
    inspected: int = 0
    def run_test(self) -> Tuple[int, int]:
        """returns the monkey to throw the item to, and the item"""
        self.inspected += 1
        next_item_worry = self.items.pop(0)
        new_worry = self.operation(next_item_worry) // 3
        if (new_worry % self.divisibility_test) == 0:
            return (self.true_throw_to, new_worry)
        return (self.false_throw_to, new_worry)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="file to read from")
    matches = parser.parse_args()
    with open(matches.input) as fptr:
        monkeys = list(parse_monkeys(fptr))
    for round in range(1, 21):
        print(f"Round {round}")
        for monkey in monkeys:
            while monkey.items:
                (thrown_to, worry) = monkey.run_test()
                # print(f"thows to {thrown_to} with worry {worry}")
                monkeys[thrown_to].items.append(worry)
        print(f"after round {round}, monkeys are holding items with these worry levels:")
        for (idx, monkey) in enumerate(monkeys):
            print(f"monkey {idx}: holding {monkey.items}, inspected {monkey.inspected} items")
    by_activity = sorted(monkeys, key=lambda m: m.inspected, reverse=True)
    (most_active, next_most) = (by_activity[0], by_activity[1])
    print(f"monkey business = {most_active.inspected} * {next_most.inspected} = {most_active.inspected * next_most.inspected}")