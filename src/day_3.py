"""
Day 3 challenge.
"""

from dataclasses import dataclass
from typing import List, Set

import utils

DATA_FILE = "day_3.txt"

@dataclass
class Rucksack():
    """
    Class representing a rucksack.
    """
    comp_1: Set[str]
    comp_2: Set[str]

    @property
    def all_items(self) -> Set[str]:
        """
        All items in the rucksack.
        """
        return self.comp_1 | self.comp_2

    def get_common_letter(self) -> str:
        """
        Get the item letter in both compartments.
        """
        common_letters = self.comp_1 & self.comp_2
        assert len(common_letters) == 1

        return common_letters.pop()

def _get_letter_priority(letter: str) -> int:
    """
    Return the priority of a letter.
    """
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    return letters.index(letter) + 1

def _parse_data_file(file_name: str) -> List[Rucksack]:
    """
    Parse the data file.
    """
    rucksacks: List[Rucksack] = []

    data_file_str = utils.read_data_file(file_name)

    # Get each rucksack
    for line in data_file_str.splitlines():
        assert len(line) % 2 == 0
        compart_len = len(line) // 2

        rucksack = Rucksack(
            set(line[0 : compart_len]), set(line[compart_len:(2 * compart_len)])
        )
        rucksacks.append(rucksack)

    return rucksacks


#
# Solution starts here
#
rucksacks = _parse_data_file(DATA_FILE)

# Part 1
total_priorities: int = 0
for rucksack in rucksacks:
    total_priorities += _get_letter_priority(rucksack.get_common_letter())

print(f"Sum of priorities (part 1): {total_priorities}")

# Part 2
total_priorities = 0

assert len(rucksacks) % 3 == 0

# Loop over each window of 3 elves, get the item in each elf's rucksack.
for i in range(len(rucksacks) // 3):
    common_items = (
        rucksacks[3 * i].all_items &
        rucksacks[3 * i + 1].all_items &
        rucksacks[3 * i + 2].all_items
    )

    assert len(common_items) == 1
    total_priorities += _get_letter_priority(common_items.pop())

print(f"Sum of priorities (part 2): {total_priorities}")
