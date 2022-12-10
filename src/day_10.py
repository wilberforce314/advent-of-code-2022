"""
Day 10 challenge.
"""

from __future__ import annotations

from dataclasses import dataclass
import enum
from typing import List, Optional

import utils

DATA_FILE = "day_10.txt"

DISPLAY_WIDTH = 40

class InstructionType(enum.Enum):
    """
    CPU instruction types.
    """
    ADD = "addx"
    NOOP = "noop"

@dataclass
class Instruction():
    """
    CPU instruction.
    """
    type: InstructionType
    val: Optional[int] = None

    def get_num_clock_cycles(self) -> int:
        """
        Get number of clock cycles for the instrution.
        """
        if self.type is InstructionType.ADD:
            clock_cycles = 2
        elif self.type is InstructionType.NOOP:
            clock_cycles = 1
        else:
            assert False

        return clock_cycles

def _parse_data_file(file_name: str) -> List[Instruction]:
    """
    Parse the input file into a list of CPU instructions.
    """
    instructions: List[Instruction] = []

    file_str = utils.read_data_file(file_name)

    for line in file_str.splitlines():
        line_tokens = line.split()

        if line_tokens[0] == "noop":
            assert len(line_tokens) == 1
            instruction = Instruction(InstructionType.NOOP)
        else:
            assert len(line_tokens) == 2
            instruction = Instruction(InstructionType.ADD, int(line_tokens[1]))

        instructions.append(instruction)

    return instructions

def _print_display(
    pixel_arr: List[bool], line_len: int = DISPLAY_WIDTH
) -> None:
    """
    Print the array of pixels as a display.
    """
    output_str = ""

    for i in range(len(pixel_arr)):
        output_str += "#" if pixel_arr[i] else "."

        if (i + 1) % line_len == 0:
            output_str += "\n"

    print(output_str)


#
# Solution starts here
#
instructions = _parse_data_file(DATA_FILE)

# Part 1
register = 1

# Add dummy '0th' cycle so that 0-indexed arrays do the right thing (this avoids
# the need to add lots of ugly (i - 1) indices everywhere).
register_values: List[int] = [1]

# Store the value of the register during each clock cycle in register_values
for instruction in instructions:
    # For the duration of the op, the register value is constant.
    for _ in range(instruction.get_num_clock_cycles()):
        register_values.append(register)

    if instruction.type is InstructionType.ADD:
        assert instruction.val is not None
        register += instruction.val

num_cycles = len(register_values)
signal_strengths = [register_values[i] * i for i in range(num_cycles)]

# Find sum of interesting signal strengths
part1_val = sum(signal_strengths[i] for i in range(20, num_cycles, 40))
print(f"Part 1: {part1_val}")

# Part 2
pixel_arr: List[bool] = []

# At each cycle, check the position of the sprite and check whether the pixel
# should be printed.
# Remove the dummy 0th cycle so that the indexing is correct for this part.
reg_values_offset = register_values[1:]
for i in range(num_cycles - 1):
    sprite_centre = reg_values_offset[i]
    row_idx = i % DISPLAY_WIDTH

    pixel_arr.append(abs(sprite_centre - row_idx) <= 1)

_print_display(pixel_arr)
