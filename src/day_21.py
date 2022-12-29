"""
Day 21 challenge.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

import utils


DATA_FILE = "day_21.txt"


class Operation(Enum):
    """
    Enum of operations.
    """
    PLUS = "+"
    MULTIPLY = "*"
    SUBTRACT = "-"
    DIVIDE = "/"
    EQUALITY_CHECK = "=="

    @classmethod
    def get_from_symbol(cls, symbol: str) -> Operation:
        """
        Get the operation from its value.
        """
        ret_op: Optional[Operation] = None

        for op in cls:
            if op.value == symbol:
                ret_op = op

        assert ret_op is not None
        return ret_op

    def calculate(self, operand_1: complex, operand_2: complex) -> complex:
        """
        Perform the operation on the given operands.

        'Equality check' returns 1 if the operands are equal, 0 otherwise.
        """
        result: complex

        if self is Operation.PLUS:
            result = operand_1 + operand_2
        elif self is Operation.SUBTRACT:
            result = operand_1 - operand_2
        elif self is Operation.MULTIPLY:
            result = operand_1 * operand_2
        elif self is Operation.DIVIDE:
            result = operand_1 / operand_2
        elif self is Operation.EQUALITY_CHECK:
            result = 1 if operand_1 == operand_2 else 0
        else:
            assert False

        return result

@dataclass()
class Monkey():
    """
    Class representing a monkey.
    """
    name: str
    number: Optional[complex] = None
    op_monkey_1: Optional[str] = None
    op_monkey_2: Optional[str] = None
    op_type: Optional[Operation] = None


def _parse_data_file(file_name: str) -> List[Monkey]:
    """
    Parse the data file into a list of monkeys.
    """
    data_file_str = utils.read_data_file(file_name)

    monkeys: List[Monkey] = []

    for line in data_file_str.splitlines():
        name, op = line.split(":")

        op_tokens = op.split()

        if len(op_tokens) == 1:
            monkey = Monkey(name=name, number=int(op_tokens[0]))
        elif len(op_tokens) == 3:
            monkey_op = Operation.get_from_symbol(op_tokens[1])
            monkey = Monkey(
                name=name,
                op_monkey_1=op_tokens[0],
                op_monkey_2=op_tokens[2],
                op_type=monkey_op
            )
        else:
            assert False

        monkeys.append(monkey)

    return monkeys

def _get_monkey_from_name(
    monkey_name: str, all_monkeys: List[Monkey]
) -> Monkey:
    """
    Given the monkey name, return the monkey from all_monkeys.
    """
    matching_monkeys = [
        monkey for monkey in all_monkeys if monkey.name == monkey_name
    ]

    assert len(matching_monkeys) == 1
    monkey = matching_monkeys[0]

    return monkey

def _get_monkey_number(
    monkey_name: str, all_monkeys: List[Monkey]
) -> complex:
    """
    Get the value a given monkey will shout.
    """
    monkey_num: complex

    monkey = _get_monkey_from_name(monkey_name, all_monkeys)

    if monkey.number is not None:
        monkey_num = monkey.number
    else:
        # Ugly asserts to keep mypy happy :(
        assert monkey.op_monkey_1 is not None
        assert monkey.op_monkey_2 is not None
        assert monkey.op_type is not None

        monkey_1_num = _get_monkey_number(monkey.op_monkey_1, all_monkeys)
        monkey_2_num = _get_monkey_number(monkey.op_monkey_2, all_monkeys)

        monkey_num = monkey.op_type.calculate(monkey_1_num, monkey_2_num)

    return monkey_num


#
# Solution starts here
#
monkeys = _parse_data_file(DATA_FILE)

# Part 1
val = _get_monkey_number("root", monkeys)
print(f"Part 1: root monkey yells {val}")

# Part 2
root_monkey = _get_monkey_from_name("root", monkeys)

# Get the children of the "root" monkey.
child1_name = root_monkey.op_monkey_1
child2_name = root_monkey.op_monkey_2
assert child1_name is not None
assert child2_name is not None

# Set the number for humn (i.e. us) to be 1j (which is the python built-in for
# i, the imaginary unit).
# This allows us to get expressions for the numbers of the children of "root" in
# terms of j (i.e. our number), which we can then equate and solve manually.
human = _get_monkey_from_name("humn", monkeys)
human.number = 1j

child1_num = _get_monkey_number(child1_name, monkeys)
child2_num = _get_monkey_number(child2_name, monkeys)

print("Sadly part 2 requires a manual step :(")
print(f"Child 1 expression: {child1_num}")
print(f"Child 2 expression: {child2_num}")
