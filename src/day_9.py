"""
Day 8 challenge.
"""

from __future__ import annotations

from dataclasses import dataclass
import enum
from typing import List, Optional, Set, Tuple

import utils

DATA_FILE = "day_9.txt"

@dataclass(frozen=True)
class Position():
    """
    Class representing a position in the grid.
    """
    x: int
    y: int

class Direction(enum.Enum):
    """
    Enum of directions.
    """
    RIGHT = "R"
    LEFT = "L"
    UP = "U"
    DOWN = "D"

    @classmethod
    def get_from_str(cls, dir_str: str) -> Direction:
        """
        Get enum from string.
        """
        out_dir : Optional[Direction] = None

        for dir in cls:
            if dir.value == dir_str:
                out_dir = dir

        assert out_dir is not None
        return out_dir

def _parse_data_file(file_name: str) -> List[Tuple[Direction, int]]:
    """
    Parse the input file into a list of moves.
    """
    moves: List[Tuple[Direction, int]] = []

    file_str = utils.read_data_file(file_name)

    for line in file_str.splitlines():
        dir_str, move_num_str = line.split()

        dir = Direction.get_from_str(dir_str)
        move_num = int(move_num_str)

        moves.append((dir, move_num))

    return moves


def _are_positions_adj(pos1: Position, pos2: Position) -> bool:
    """
    Check if two positions are adjacent.
    """
    return abs(pos1.x - pos2.x) <= 1 and abs(pos1.y - pos2.y) <= 1

def _get_new_head_pos(dir: Direction, start_pos: Position) -> Position:
    """
    Get the new head position given a direction and start position.
    """
    x = start_pos.x
    y = start_pos.y

    if dir is Direction.UP:
        y += 1
    elif dir is Direction.DOWN:
        y -= 1
    elif dir is Direction.LEFT:
        x -= 1
    elif dir is Direction.RIGHT:
        x += 1
    else:
        assert False

    return Position(x, y)

def _get_new_tail_pos(head_pos: Position, start_tail_pos: Position) -> Position:
    """
    Given the current head/tail positions, get the new tail position after
    chasing the head.
    """
    x = start_tail_pos.x
    y = start_tail_pos.y

    # Don't move the tail if it is already adjacent. Otherwise, chase at most 1
    # in each of the x and y directions, if required.
    if not _are_positions_adj(head_pos, start_tail_pos):
        # If the tail's x value is different, chase by 1
        if head_pos.x > start_tail_pos.x:
            x += 1
        elif head_pos.x < start_tail_pos.x:
            x -= 1

        # If the tail's y value is different, chase by 1
        if head_pos.y > start_tail_pos.y:
            y += 1
        elif head_pos.y < start_tail_pos.y:
            y -= 1

    new_tail_pos = Position(x, y)
    assert _are_positions_adj(head_pos, new_tail_pos)

    return new_tail_pos

#
# Solution starts here
#
moves = _parse_data_file(DATA_FILE)

# Part 1
head_pos = Position(0, 0)
tail_pos = Position(0, 0)

tail_positions: Set[Position] = set()
tail_positions.add(tail_pos)

# Simulate the moves:
for move in moves:
    for _ in range(move[1]):
        head_pos = _get_new_head_pos(move[0], head_pos)
        tail_pos = _get_new_tail_pos(head_pos, tail_pos)
        tail_positions.add(tail_pos)

print(f"Part 1, number of tail positions: {len(tail_positions)}")

# Part 2
num_knots = 10
knot_positions: List[Position] = [Position(0, 0) for _ in range(num_knots)]

tail_positions_part2: Set[Position] = set()

# Simulate the moves:
for move in moves:
    # Do the number of U/D/L/R moves suggested.
    for _ in range(move[1]):
        # Move the head
        knot_positions[0] = _get_new_head_pos(move[0], knot_positions[0])

        # Update each of the other knots, which follow the previous knot in the
        # rope.
        for i in range(num_knots - 1):
            knot_positions[i + 1] = _get_new_tail_pos(
                knot_positions[i], knot_positions[i + 1]
            )

        # Add to the set tracking where the furthest back tail ended up.
        tail_positions_part2.add(knot_positions[num_knots - 1])

print(f"Part 2, number of tail positions: {len(tail_positions_part2)}")
