"""
Day 1 challenge.
"""

import heapq
from typing import List

import utils

DATA_FILE = "day_1.txt"


def _parse_data_file(file_name: str) -> List[List[int]]:
    """
    Parse the data file, return a list of calories for each elf.
    """
    data_str = utils.read_data_file(file_name)

    calories_per_elf_str = data_str.split("\n\n")

    return [
        [int(calorie_val) for calorie_val in elf_str.splitlines()]
        for elf_str in calories_per_elf_str
    ]

def _print_part_1(per_elf_calories: List[List[int]]) -> None:
    """
    Print part 1 solution.
    """
    calorie_sums = [sum(elf_calories) for elf_calories in per_elf_calories]

    print(f"Most calories carried by an elf: {max(calorie_sums)}")

def _print_part_2(per_elf_calories: List[List[int]]) -> None:
    """
    Print part 2 solution.
    """
    calorie_sums = [sum(elf_calories) for elf_calories in per_elf_calories]

    top_three_sums = heapq.nlargest(3, calorie_sums)
    print(f"Sum of top three largest calorie sums: {sum(top_three_sums)}")

def main() -> None:
    """
    Print the solutions.
    """
    # Get a list of lists, where each inner list is the list of food calories
    # for a particular elf.
    calories_list = _parse_data_file(DATA_FILE)

    _print_part_1(calories_list)
    _print_part_2(calories_list)

if __name__ == '__main__':
    main()
