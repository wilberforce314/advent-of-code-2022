"""
Day 5 challenge.
"""

from copy import deepcopy
from dataclasses import dataclass
import re
from typing import List, Tuple

import utils

DATA_FILE = "day_5.txt"


@dataclass
class StackOperation():
    """
    A single stack operation.
    """
    start_stack: int
    end_stack: int
    num_moved: int

def _parse_stack_lines(stack_lines: List[str]) -> List[List[str]]:
    """
    Parse the lines in the input representing the stacks.
    """
    def _get_num_of_stacks_in_line(line: str) -> int:
        assert (len(line) + 1) % 4 == 0
        return (len(line) + 1) // 4

    num_stacks = max(
        _get_num_of_stacks_in_line(line) for line in stack_lines
    )
    stacks: List[List[str]] = [[] for _ in range(num_stacks)]

    for line in reversed(stack_lines):
        num_stacks = _get_num_of_stacks_in_line(line)

        # Check if each stack is there. If not, the section of output should be
        # blank.
        for i in range(num_stacks):
            stack_pattern = r"\[([A-Z])\]"
            stack_str = line[4*i : 4*(i + 1)]

            stack_match = re.match(stack_pattern, stack_str)
            if stack_match is not None:
                stacks[i].append(stack_match.group(1))
            else:
                assert stack_str == "    "

    return stacks

def _parse_data_file(file_name: str) -> Tuple[
    List[List[str]], List[StackOperation]
]:
    """
    Parse the data file into a list of stacks and a list of stack operations.
    """
    data_file_str = utils.read_data_file(file_name)

    stack_operations: List[StackOperation] = []
    stacks: List[List[str]] = []

    operation_pattern = r"move (\d+) from (\d+) to (\d+)"
    stack_line_pattern = r"(\s*\[[A-Z]\]\s*)+"

    stack_lines: List[str] = []

    for line in data_file_str.splitlines():
        op_match = re.match(operation_pattern, line)

        # Add to the set of operations, if this is an operation line.
        if op_match is not None:
            operation = StackOperation(
                start_stack=int(op_match.group(2)),
                end_stack=int(op_match.group(3)),
                num_moved=int(op_match.group(1))
            )
            stack_operations.append(operation)

        # Add to the list of stack lines, if this is a stack line.
        stack_line_match = re.match(stack_line_pattern, line)
        if stack_line_match:
            stack_lines.append(line)

    stacks = _parse_stack_lines(stack_lines)

    return stacks, stack_operations

def _perform_stack_operation_9000(
    stacks: List[List[str]], op: StackOperation
) -> None:
    """
    Perform the given stack operation on `stacks`.
    """
    for _ in range(op.num_moved):
        crate = stacks[op.start_stack - 1].pop()
        stacks[op.end_stack - 1].append(crate)

def _perform_stack_operation_9001(
    stacks: List[List[str]], op: StackOperation
) -> None:
    """
    Perform the given stack operation on `stacks`.
    """
    crates_to_move = stacks[op.start_stack - 1][-op.num_moved : ]

    stacks[op.start_stack - 1] = (
        stacks[op.start_stack - 1][ : -op.num_moved]
    )
    stacks[op.end_stack - 1].extend(crates_to_move)

def _get_top_of_stacks_str(stacks: List[List[str]]) -> str:
    """
    Get string representing the stacks top.
    """
    top_of_stack_str = ""
    for stack in stacks:
        top_of_stack_str += stack[-1] if stack else " "

    return top_of_stack_str


#
# Solution starts here
#
stacks, operations = _parse_data_file(DATA_FILE)

# Part 1
stacks_copy = deepcopy(stacks)
for op in operations:
    _perform_stack_operation_9000(stacks_copy, op)

top_of_stack_str = _get_top_of_stacks_str(stacks_copy)
print(f"Top of each stack (part 1): {top_of_stack_str}")

# Part 2
stacks_copy = deepcopy(stacks)
for op in operations:
    _perform_stack_operation_9001(stacks_copy, op)

top_of_stack_str = _get_top_of_stacks_str(stacks_copy)
print(f"Top of each stack (part 2): {top_of_stack_str}")
