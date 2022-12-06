"""
Day 6 challenge.
"""

from typing import Optional

import utils

DATA_FILE = "day_6.txt"

def _get_start_of_packet_marker(
    input_str: str, seq_len: int = 4
) -> Optional[int]:
    """
    Return the index of the start-of-packet-marker in input_str.
    """
    marker_idx: Optional[int] = None
    input_len = len(input_str)

    for i in range(0, input_len - seq_len):
        candidate_seq = input_str[i : (i + seq_len)]
        if len(set(candidate_seq)) == seq_len:
            marker_idx = i + seq_len
            break

    return marker_idx

#
# Solution starts here
#
input_str = utils.read_data_file(DATA_FILE).strip()

# Part 1
marker = _get_start_of_packet_marker(input_str)
print(f"Part 1: marker is {marker}")

# Part 2
marker = _get_start_of_packet_marker(input_str, seq_len=14)
print(f"Part 2: marker is {marker}")
