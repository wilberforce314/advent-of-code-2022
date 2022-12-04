"""
Day 4 challenge.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import utils

DATA_FILE = "day_4.txt"

@dataclass
class SectionRange():
    """
    A range of sections assigned to a single elf.
    """
    start: int
    end: int

    def contains_range(self, other_range: SectionRange) -> bool:
        """
        Check if this section range contains another section range.
        """
        return self.start <= other_range.start and self.end >= other_range.end

    def is_in_range(self, section: int) -> bool:
        """
        Check if the section number `section` appears in this range.
        """
        return self.start <= section and section <= self.end

    def does_range_overlap(self, other_range: SectionRange) -> bool:
        """
        Check if this range overlaps with other_range.
        """
        # Check if either range endpoint appears in the other range.
        return (
            other_range.is_in_range(self.start) or
            other_range.is_in_range(self.end) or
            self.is_in_range(other_range.start) or
            self.is_in_range(other_range.end)
        )

def _parse_data_file(file_name: str) -> List[Tuple[SectionRange, SectionRange]]:
    """
    Parse the data file, return a list of tuples, where each tuple is:
        (<section range for elf 1 in pair>, <section range for elf 2 in pair>)
    """
    pair_ranges: List[Tuple[SectionRange, SectionRange]] = []

    data_file_str = utils.read_data_file(file_name)

    def _get_range_from_str(range_str: str) -> SectionRange:
        """
        Parse the range from a string such as "26-69".
        """
        start, end = range_str.split("-")
        return SectionRange(int(start), int(end))

    for line in data_file_str.splitlines():
        range1, range2 = line.split(",")

        pair = (_get_range_from_str(range1), _get_range_from_str(range2))
        pair_ranges.append(pair)

    return pair_ranges

#
# Solution starts here
#
pair_ranges = _parse_data_file(DATA_FILE)

# Part 1
superset_pair_num = 0
for range1, range2 in pair_ranges:
    if range1.contains_range(range2) or range2.contains_range(range1):
        superset_pair_num += 1

print(
    f"Number of pairs with one range containing the other: {superset_pair_num}"
)

# Part 2
overlap_pair_num = 0
for range1, range2 in pair_ranges:
    if range1.does_range_overlap(range2):
        overlap_pair_num += 1

print(f"Number of overlapping pairs: {overlap_pair_num}")
