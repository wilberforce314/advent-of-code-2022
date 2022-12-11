"""
Day 11 challenge.
"""

from __future__ import annotations

from dataclasses import dataclass
import enum
from math import gcd
import queue
import re
from textwrap import dedent
from typing import Callable, Generator, List, Optional, Sequence, Union

import utils

DATA_FILE = "day_11.txt"

MONKEY_PATTERN = r"""
Monkey (?P<num>\d+):
  Starting items: (?P<item_list>[\d, ]+)
  Operation: (?P<op_str>[^\n]+)
  Test: divisible by (?P<test_num>\d+)
    If true: throw to monkey (?P<true_num>\d+)
    If false: throw to monkey (?P<false_num>\d+)
"""

class OpType(enum.Enum):
    MULTIPLY = "*"
    ADD = "+"
    SQUARE = "^2"

@dataclass
class Monkey():
    """
    Class representing a monkey.
    """
    num: int
    item_levels: queue.Queue
    op: Callable[[int], int]
    test: Callable[[int], bool]
    next_hop_true: int
    next_hop_false: int
    item_inspect_count: int = 0

@dataclass
class Monkey2():
    """
    Class representing a monkey for part 2.
    """
    num: int
    item_levels: List[int]
    op_type: OpType
    op_val: Optional[int]
    test_val: int
    next_hop_true: int
    next_hop_false: int
    item_inspect_count: int = 0

EitherMonkey = Union[Monkey, Monkey2]

def _calculate_lcm(*vals: int) -> int:
    """
    Get the LCM of a list of values.
    """
    lcm: int

    if len(vals) == 2:
        lcm = abs(vals[0] * vals[1]) // gcd(vals[0], vals[1])
    else:
        lcm = _calculate_lcm(vals[0], _calculate_lcm(*vals[1:]))

    return lcm

def _get_monkey_matches(file_name: str) -> Generator[re.Match, None, None]:
    """
    Get strings matching MONKEY_PATTERN in file_name.
    """
    file_str = utils.read_data_file(file_name)

    # This is horrible, but necessary due to the weird interaction between the
    # "\" used by textwrap to ignore the first blank line, and the special
    # treatment of "\" in raw strings.
    monkey_pattern = dedent(MONKEY_PATTERN[1:])

    for m in re.finditer(monkey_pattern, file_str):
        yield m

def _parse_data_file_part1(file_name: str) -> List[Monkey]:
    """
    Parse the input file into a list of monkeys for part 1.
    """
    monkeys: List[Monkey] = []

    def get_monkey_from_match(match: re.Match) -> Monkey:
        """
        From a match of the re string above, return a monkey object.
        """
        # Parse the monkey's number.
        num = int(match.group("num"))

        # Parse the monkey's starting items.
        item_list_str = match.group("item_list")
        item_list = [int(item_num) for item_num in item_list_str.split(", ")]

        # Parse the operation.
        op_tokens = match.group("op_str").split()
        assert op_tokens[:3] == ["new", "=", "old"]

        def monkey_op(in_val: int) -> int:
            other_val = in_val if op_tokens[4] == "old" else int(op_tokens[4])

            if op_tokens[3] == "+":
                out_val = in_val + other_val
            elif op_tokens[3] == "*":
                out_val = in_val * other_val
            else:
                assert False

            return out_val

        # Parse the test operation.
        test_num = int(match.group("test_num"))
        test_op = lambda x: x % test_num == 0

        # Parse the next op monkey nums (depending on test op outcome).
        next_hop_true = int(match.group("true_num"))
        next_hop_false = int(match.group("false_num"))

        monkey = Monkey(
            num=num,
            item_levels=queue.Queue(),
            op=monkey_op,
            test=test_op,
            next_hop_true=next_hop_true,
            next_hop_false=next_hop_false
        )

        for level in item_list:
            monkey.item_levels.put(level)

        return monkey

    for match in _get_monkey_matches(file_name):
        monkeys.append(get_monkey_from_match(match))

    monkeys.sort(key=lambda x: x.num)
    return monkeys

def _parse_data_file_part2(file_name: str) -> List[Monkey2]:
    """
    Parse the input file into a list of monkeys for part 2.
    """
    monkeys: List[Monkey2] = []

    def get_monkey_from_match(match: re.Match) -> Monkey2:
        """
        From a match of the re string above, return a monkey object.
        """
        # Parse the monkey's number.
        num = int(match.group("num"))

        # Parse the monkey's starting items.
        item_list_str = match.group("item_list")
        item_list = [int(item_num) for item_num in item_list_str.split(", ")]

        # Parse the operation.
        op_val: Optional[int] = None

        op_tokens = match.group("op_str").split()
        assert op_tokens[:3] == ["new", "=", "old"]

        if op_tokens[4] == "old":
            # Squaring the old value.
            assert op_tokens[3] == "*"
            op_type = OpType.SQUARE
        else:
            # Adding or multiplying a fixed value.
            if op_tokens[3] == "+":
                op_type = OpType.ADD
            else:
                assert op_tokens[3] == "*"
                op_type = OpType.MULTIPLY
            op_val = int(op_tokens[4])

        # Parse the test operation.
        test_num = int(match.group("test_num"))

        # Parse the next op monkey nums (depending on test op outcome).
        next_hop_true = int(match.group("true_num"))
        next_hop_false = int(match.group("false_num"))

        monkey = Monkey2(
            num=num,
            item_levels=item_list,
            op_type=op_type,
            op_val=op_val,
            test_val=test_num,
            next_hop_true=next_hop_true,
            next_hop_false=next_hop_false
        )

        return monkey

    for match in _get_monkey_matches(file_name):
        monkeys.append(get_monkey_from_match(match))

    monkeys.sort(key=lambda x: x.num)
    return monkeys

def _get_monkey_from_list(
    monkeys: Sequence[EitherMonkey], monkey_num: int
) -> EitherMonkey:
    """
    Get the monkey in monkeys with the given num.
    """
    matching_monkeys = [
        monkey for monkey in monkeys if monkey.num == monkey_num
    ]
    assert len(matching_monkeys) == 1

    return matching_monkeys[0]

def _simulate_round_part1(monkeys: Sequence[Monkey]) -> None:
    """
    Simulate a single round for part 1.
    """
    for monkey in monkeys:
        # Process a single monkey.
        while not monkey.item_levels.empty():
            item_level = monkey.item_levels.get()

            # Adjust the worry level for the item being inspected.
            # Unfortunately this confuses mypy :(
            item_level = monkey.op(item_level)          # type: ignore

            # Divide by 3 after the inspection finishes.
            item_level = item_level // 3

            # Perform the test to see where the item goes next.
            # Again, this confuses mypy :(
            test_outcome = monkey.test(item_level)      # type: ignore

            next_monkey = _get_monkey_from_list(
                monkeys,
                monkey.next_hop_true if test_outcome else monkey.next_hop_false
            )
            assert isinstance(next_monkey, Monkey)
            next_monkey.item_levels.put(item_level)

            # Add to the monkey's count.
            monkey.item_inspect_count += 1

def _simulate_round_part2(monkeys: Sequence[Monkey2], modulo_size: int) -> None:
    """
    Simulate a single round for part 2.
    """
    for monkey in monkeys:
        # Process a single monkey.
        while monkey.item_levels:
            item_level = monkey.item_levels.pop()

            # Adjust the worry level for the item being inspected.
            if monkey.op_type == OpType.SQUARE:
                item_level = item_level ** 2
            elif monkey.op_type == OpType.ADD:
                assert monkey.op_val is not None
                item_level = item_level + monkey.op_val
            else:
                assert monkey.op_val is not None
                item_level = item_level * monkey.op_val

            # Scale back down the worry level.
            item_level = item_level % modulo_size

            # Perform the test to see where the item goes next.
            test_outcome = (item_level % monkey.test_val == 0)

            next_monkey = _get_monkey_from_list(
                monkeys,
                monkey.next_hop_true if test_outcome else monkey.next_hop_false
            )
            assert isinstance(next_monkey, Monkey2)
            next_monkey.item_levels = [item_level] + next_monkey.item_levels

            # Add to the monkey's count.
            monkey.item_inspect_count += 1

#
# Solution starts here
#
# Part 1 - simulate 20 rounds
monkeys_1 = _parse_data_file_part1(DATA_FILE)
for _ in range(20):
    _simulate_round_part1(monkeys_1)

monkey_activites = [monkey.item_inspect_count for monkey in monkeys_1]
monkey_activites.sort(reverse=True)

part1_total = monkey_activites[0] * monkey_activites[1]
print(f"Part 1 monkey business: {part1_total}")

# Part 2 - simulate 10000 rounds. Part 2 is annoying, so parse the monkeys into
#          a different dataclass.
monkeys_2 = _parse_data_file_part2(DATA_FILE)

# We don't care about the exact values of the worry levels, only that the items
# end up at the right monkey after each test. For that reason, here we choose to
# do arithmetic modulo some value which will not affect the test calculations.
#
# Choose the LCM of the of the test values (i.e. the numbers we divide by when
# checking which monkey to send an item to next).
test_vals = [monkey.test_val for monkey in monkeys_2]
lcm = _calculate_lcm(*test_vals)

for _ in range(10000):
    _simulate_round_part2(monkeys_2, modulo_size=lcm)

monkey_activites = [monkey.item_inspect_count for monkey in monkeys_2]
monkey_activites.sort(reverse=True)

part2_total = monkey_activites[0] * monkey_activites[1]
print(f"Part 2 monkey business: {part2_total}")
