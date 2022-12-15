"""
Day 13 challenge.
"""

import ast
from dataclasses import dataclass
from enum import Enum
from typing import Any, List

import utils

DATA_FILE = "day_13.txt"

PKT = List[Any]

class CompareResult(Enum):
    """
    Results of a comparison (i.e. which is smaller?: left, right, or neither).
    """
    LEFT="left"
    EQUAL="equal"
    RIGHT="right"


@dataclass
class PacketPair():
    """
    Class representing a packet pair.
    """
    packet_1: PKT
    packet_2: PKT


def _get_packet_order(packet1: PKT, packet2: PKT) -> CompareResult:
    """
    Get the result of comparing packet1 and packet2.
    """
    result: CompareResult

    def _convert_to_list_if_req(element: Any) -> List:
        """
        Convert element to a list if it is an integer, leave it alone if it is
        already a list.
        i.e.    2       -> [2]
                [1,2,3] -> [1,2,3]
        """
        if isinstance(element, int):
            element = [element]
        else:
            assert isinstance(element, list)

        return element

    if not packet1 and not packet2:
        # Both are empty
        result = CompareResult.EQUAL
    elif not packet1:
        # Only packet1 is out of values.
        result = CompareResult.LEFT
    elif not packet2:
        # Only packet2 is out of values.
        result = CompareResult.RIGHT
    else:
        # packet1 and packet2 are both non-empty. Get the head elements.
        packet1_head = packet1[0]
        packet2_head = packet2[0]

        if isinstance(packet1_head, int) and isinstance(packet2_head, int):
            # Compare the head elements of the packets, which are ints.
            if packet1_head < packet2_head:
                result = CompareResult.LEFT
            elif packet1_head > packet2_head:
                result = CompareResult.RIGHT
            else:
                # If the head elements are equal, compare the rest of the
                # packets.
                result = _get_packet_order(packet1[1:], packet2[1:])
        else:
            # At least one of the head elements is a list. Convert them
            # both to lists, and compare them:
            # - if they are the same, compare the rest of the lists.
            # - if they differ, the overall result is the same as the
            #   head element comparison.
            packet1_list = _convert_to_list_if_req(packet1_head)
            packet2_list = _convert_to_list_if_req(packet2_head)

            head_cmp_result = _get_packet_order(
                packet1_list, packet2_list
            )
            if head_cmp_result is CompareResult.EQUAL:
                result = _get_packet_order(packet1[1:], packet2[1:])
            else:
                result = head_cmp_result

    return result

def _packets_are_in_order(packet1: PKT, packet2: PKT) -> bool:
    """
    Return True if packet1 and packet2 are in order, False otherwise.
    """
    order = _get_packet_order(packet1, packet2)

    return order in {CompareResult.LEFT, CompareResult.EQUAL}

def _insert_pkt_in_sorted_list(sorted_pkts: List[PKT], new_pkt: PKT) -> None:
    """
    Insert new_pkt in the correct location in the sorted list sorted_pkts.
    """
    insert_idx = 0
    while (
        insert_idx < len(sorted_pkts) and
        not _packets_are_in_order(new_pkt, sorted_pkts[insert_idx])
    ):
        insert_idx += 1

    sorted_pkts.insert(insert_idx, new_pkt)

def _parse_data_file_part1(file_name: str) -> List[PacketPair]:
    """
    Parse the data file into an array of packet pairs for part 1.
    """
    pairs: List[PacketPair] = []

    data_file_str = utils.read_data_file(file_name)

    # Spilt by double blank lines to get packet pairs.
    for pair in data_file_str.split("\n\n"):
        pair_lines = pair.splitlines()
        assert len(pair_lines) == 2

        new_pair = PacketPair(
            packet_1=ast.literal_eval(pair_lines[0]),
            packet_2=ast.literal_eval(pair_lines[1])
        )
        pairs.append(new_pair)

    return pairs

def _parse_data_file_part2(file_name: str) -> List[PKT]:
    """
    Parse the data file into an array of packets for part 2.
    """
    packets: List[PKT] = []

    data_file_str = utils.read_data_file(file_name)

    # Parse each line, ignoring blank lines.
    packets = [
        ast.literal_eval(line) for line in data_file_str.splitlines() if line
    ]

    return packets


#
# Solution starts here
#
# Part 1
pairs = _parse_data_file_part1(DATA_FILE)
indices_sum = sum(
    i + 1 for i in range(len(pairs))
    if _packets_are_in_order(pairs[i].packet_1, pairs[i].packet_2)
)
print(f"Part 1 indices sum: {indices_sum}")

# Part 2
packets = _parse_data_file_part2(DATA_FILE)

# Apparently python doesn't have a built-in sorter when only pairwise comparison
# of elements is available- wtf?
sorted_pkts: List[PKT] = []
for packet in packets:
    _insert_pkt_in_sorted_list(sorted_pkts, packet)

# Insert the new packets.
new_pkt_1 = [[2]]
new_pkt_2 = [[6]]

_insert_pkt_in_sorted_list(sorted_pkts, new_pkt_1)
_insert_pkt_in_sorted_list(sorted_pkts, new_pkt_2)

idx1 = sorted_pkts.index(new_pkt_1)
idx2 = sorted_pkts.index(new_pkt_2)

print(f"Part 2, decoder key: {(idx1 + 1) * (idx2 + 1)}")
