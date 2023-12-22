"""
Day 24 challenge.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Union, Tuple

import utils
from utils import Direction, Point


DATA_FILE = "day_24_test.txt"


@dataclass
class ValleyCell():
    """
    Class representing a single point in the valley.

    blizzards is a dict mapping direction to bool indicating whether or not a
    blizzard with that direction is in the cell.
    """
    is_wall: bool = False
    blizzards: Dict[Direction, bool] = field(
        default_factory=(lambda: defaultdict(bool))
    )

    def __str__(self) -> str:
        """
        String representation.
        """
        if self.is_wall:
            return "#"

        # Not a wall - work out how many blizzards.
        dir_to_str_map = {
            Direction.EAST : ">",
            Direction.NORTH : "^",
            Direction.WEST : "<",
            Direction.SOUTH : "v"
        }

        included_dirs = [
            blizzard_dir for blizzard_dir in self.blizzards
            if self.blizzards[blizzard_dir]
        ]

        if len(included_dirs) == 0:
            return "."
        elif len(included_dirs) >= 2:
            return str(len(included_dirs))
        else:
            return dir_to_str_map[included_dirs[0]]

    @property
    def contains_blizzard(self) -> bool:
        """
        Does the cell contain a blizzard.
        """
        return any(self.blizzards[dirn] for dirn in Direction)


# Type for an object representing the entire valley, including walls.
ValleyType = List[List[ValleyCell]]

# Cache for the state of the valley at each step.
valley_cache: List[ValleyType] = []


# Type of an array representing the safe cells in the valley (including walls,
# which are deemed not safe).
SafeCellArrayType = List[List[bool]]

# Cache indicating which cells are safe at each step.
safe_cell_cache: List[SafeCellArrayType] = []


def _parse_data_file_line(line: str) -> List[ValleyCell]:
    """
    Parse a single line in the data file.
    """
    row: List[ValleyCell] = []

    blizzard_map = {
        ">" : Direction.EAST,
        "^" : Direction.NORTH,
        "<" : Direction.WEST,
        "v" : Direction.SOUTH
    }

    for char in line:
        blizzards = {dir: False for dir in Direction}

        if char == "#":
            cell = ValleyCell(is_wall=True)
        elif char == ".":
            cell = ValleyCell(blizzards=blizzards)
        else:
            blizzards[blizzard_map[char]] = True
            cell = ValleyCell(blizzards=blizzards)

        row.append(cell)

    return row

def _parse_data_file(file_name: str) -> ValleyType:
    """
    Parse the data file.
    """
    data_file_str = utils.read_data_file(file_name)
    lines = data_file_str.splitlines()

    return [_parse_data_file_line(line) for line in lines]


def _print_valley(valley: ValleyType) -> None:
    """
    Print a valley.
    """
    for row in valley:
        for cell in row:
            print(cell, end="")
        print("")

def _print_safe_cell_matrix(safe_cell_matrix: SafeCellArrayType) -> None:
    """
    Print a 'safe cell matrix'.
    """
    for row in safe_cell_matrix:
        for safe_result in row:
            if safe_result:
                print("Y", end="")
            else:
                print("N", end="")
        print("")

#
# Helpers for simulating the blizzards
#

def _get_wall_equiv(valley: ValleyType, wall_coords: Point) -> Point:
    """
    This is a bit obscure, and a bit gross.

    Given the coords of a wall, get the point that a blizzard actually goes to
    if it would normally have travelled to wall_coords, if it weren't a wall.
    """
    num_rows, num_cols = _get_valley_size(valley)

    new_x = wall_coords.x
    new_y = wall_coords.y

    # Need to wrap the x.
    if new_x == 0:
        new_x = num_rows - 2
    elif new_x == num_rows - 1:
        new_x = 1

    # Need to wrap the y
    if new_y == 0:
        new_y = num_cols - 2
    elif new_y == num_cols - 1:
        new_y = 1

    return Point(new_x, new_y)

def _get_surrounding_cells(
    valley: ValleyType, cell_coords: Point
) -> Dict[Direction, ValleyCell]:
    """
    Given a valley, return a dict of the form:
       { direction : cell_val }

    Where direction is the direction to get *from the neighbor to cell_coords*,
    and cell_val is the value.

    The dict returned only includes valley cells, not walls.
    """
    num_rows, _ = _get_valley_size(valley)

    # Special case for the entry/exit points, which can never contain any
    # blizzards - so don't care what the surrounding cells are.
    if cell_coords.x == 0 or cell_coords.x == num_rows - 1:
        return {}

    # Slightly funny dictionary:
    #   Keys: direction from neighbor to cell_coords
    #   Values: step from cell_coords to neighboring point
    nbh_steps: Dict[Direction, Point] = {
        Direction.SOUTH: Point(-1, 0),
        Direction.NORTH: Point(1, 0),
        Direction.EAST: Point(0, -1),
        Direction.WEST: Point(0, 1)
    }

    out_dict: Dict[Direction, ValleyCell] = {}
    for dirn, step in nbh_steps.items():
        nbh_point = cell_coords + step
        nbh_cell = valley[nbh_point.x][nbh_point.y]

        if nbh_cell.is_wall:
            # Neighbor is a wall. We need to 'wrap around', pacman style.
            nbh_point = _get_wall_equiv(valley, nbh_point)
            nbh_cell = valley[nbh_point.x][nbh_point.y]

        out_dict[dirn] = nbh_cell

    return out_dict

def _get_valley_size(valley: ValleyType) -> Tuple[int, int]:
    """
    Get the size of the valley as (num_rows, num_cols).
    """
    return (len(valley), len(valley[0]))

def _simulate_valley_step_single_cell(
    curr_valley: ValleyType, coords: Point
) -> ValleyCell:
    """
    Get the new value of a single cell, given the current value of the cell.
    """
    curr_cell = curr_valley[coords.x][coords.y]

    if curr_cell.is_wall:
        # Wall cells do not change
        return ValleyCell(is_wall=True)
    else:
        blizzards_dict = {dirn: False for dirn in Direction}

        nbhs_dict = _get_surrounding_cells(curr_valley, coords)

        for dirn, cell_val in nbhs_dict.items():
            if cell_val.blizzards[dirn]:
                blizzards_dict[dirn] = True

        return ValleyCell(blizzards=blizzards_dict)

def _simulate_valley_step(curr_valley: ValleyType) -> ValleyType:
    """
    Simulate the valley moving forward 1 step in time, given the current state
    of the valley. Return the new state of the valley.
    """
    num_rows, num_cols = _get_valley_size(curr_valley)

    return [
        [
            _simulate_valley_step_single_cell(curr_valley, Point(row, col))
            for col in range(num_cols)
        ]
        for row in range(num_rows)
    ]

def _get_valley(step: int) -> ValleyType:
    """
    Get the state of the valley at a given step.
    """
    global valley_cache

    try:
        valley = valley_cache[step]
    except IndexError:
        # Not yet in cache. Need to simulate next step and add to the cache.
        prev_valley = _get_valley(step - 1)
        valley = _simulate_valley_step(prev_valley)

        # At this point, the valley cache should be populated up until `step`.
        assert len(valley_cache) == step
        valley_cache.append(valley)

    return valley

def _calculate_safe_cells_matrix(valley: ValleyType) -> SafeCellArrayType:
    """
    Calculate the matrix of safe cells from the current valley.
    """
    return [
        [not cell.contains_blizzard and not cell.is_wall for cell in row]
        for row in valley
    ]

def _get_safe_cells_matrix(step: int) -> SafeCellArrayType:
    """
    Get the cell safety matrix.
    """
    global safe_cell_cache

    try:
        safe_cell_matrix = safe_cell_cache[step]
    except IndexError:
        # Not yet in cache. Presumably the cache should at least be filled up to
        # (step - 1).
        assert len(safe_cell_cache) == step

        valley = _get_valley(step)
        safe_cell_matrix = _calculate_safe_cells_matrix(valley)
        safe_cell_cache.append(safe_cell_matrix)

    return safe_cell_matrix


#
# Solution starts here
#
# Part 1
initial_valley = _parse_data_file(DATA_FILE)
valley_cache.append(initial_valley)

for i in range(5):
    print(f"STEP {i}")
    valley = _get_valley(i)
    _print_valley(valley)
    print("")
    safe_cell_matrix = _get_safe_cells_matrix(i)
    _print_safe_cell_matrix(safe_cell_matrix)
    print("")

print(f"STEP 2")
valley = _get_valley(2)
_print_valley(valley)
print("")
safe_cell_matrix = _get_safe_cells_matrix(2)
_print_safe_cell_matrix(safe_cell_matrix)
print("")
