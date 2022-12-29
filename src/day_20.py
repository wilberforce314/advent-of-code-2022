"""
Day 20 challenge.
"""

from typing import List

import utils


DATA_FILE = "day_20.txt"


def _parse_data_file(file_name: str) -> List[int]:
    """
    Parse the data file into a list of integers.
    """
    data_file_str = utils.read_data_file(file_name)

    return [int(line) for line in data_file_str.splitlines()]

def _simulate_update(
    idx: int, numbers: List[int], index_mapping: List[int]
) -> None:
    """
    Simulate an update in the circular array for the number with index `idx` in
    the original array.
    """
    numbers_len = len(numbers)

    # Find the number we want to move in the circular array from `idx` (its
    # index in the original array), and remove it from the mapping.
    circle_arr_idx = index_mapping.index(idx)
    index_mapping.pop(circle_arr_idx)

    # Update the index of the number in the circular array by its value. Note
    # that, after the .pop() above, the length of index_mapping is now
    # (numbers_len - 1).
    circle_arr_idx += numbers[idx]
    circle_arr_idx = circle_arr_idx % (numbers_len - 1)

    # Insert the number's original back into the index mapping, at the number's
    # new position in the circular array.
    index_mapping.insert(circle_arr_idx, idx)

def _get_grove_coordinates(
    numbers: List[int], index_mapping: List[int]
) -> List[int]:
    """
    Get the grove coordinates- i.e. the 1000th, 2000th and 3000th values after
    0 in the circular array.
    """
    numbers_len = len(numbers)

    # Get the index of 0 in the original array and the circular array.
    zero_idx = numbers.index(0)
    zero_circular_idx = index_mapping.index(zero_idx)

    # Find each coordinate.
    coords: List[int] = []
    for offset in [1000, 2000, 3000]:
        circular_idx = (zero_circular_idx + offset) % numbers_len
        coords.append(numbers[index_mapping[circular_idx]])

    return coords

def _print_circular_arr(numbers: List[int], index_mapping: List[int]) -> None:
    """
    Print the circular array.
    """
    out_arr = [numbers[index_mapping[i]] for i in range(len(numbers))]
    print(out_arr)


#
# Solution starts here
#
numbers = _parse_data_file(DATA_FILE)
numbers_len = len(numbers)

# Part 1
# `numbers` gives the numbers in their original order.
# The i'th value in `index_mapping` gives the index in the original array of the
# i'th number in the circular array.
index_mapping = list(range(numbers_len))

# Simulate an update for each number.
for i in range(numbers_len):
    _simulate_update(i, numbers, index_mapping)

coords = _get_grove_coordinates(numbers, index_mapping)
print(f"Part 1: {sum(coords)}")

# Part 2
numbers = [number * 811589153 for number in numbers]
index_mapping = list(range(numbers_len))

# Simulate the mixing.
for _ in range(10):
    for i in range(numbers_len):
        _simulate_update(i, numbers, index_mapping)

coords = _get_grove_coordinates(numbers, index_mapping)
print(f"Part 2: {sum(coords)}")
