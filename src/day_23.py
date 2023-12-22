"""
Day 23 challenge.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Set

import utils
from utils import Direction, Point


DATA_FILE = "day_23_test.txt"


def _parse_data_file(file_name: str) -> Set[Point]:
    """
    Parse the data file into a list of elves.
    """
    elf_locations: Set[Point] = set()

    data_file_str = utils.read_data_file(file_name)
    lines = data_file_str.splitlines()

    for row_num in range(len(lines)):
        line = lines[row_num]
        line_len = len(line)

        for col_num in range(line_len):
            symbol = line[col_num]

            if symbol == "#":
                elf_locations.add(Point(row_num, col_num))
            else:
                assert symbol == "."

    return elf_locations

def _get_next_direction(cur_dir: Direction) -> Direction:
    """
    Get the next direction the elves would inspect after the current direction.
    """
    dirs = [dir for dir in Direction]
    cur_dir_idx = dirs.index(cur_dir)

    return dirs[(cur_dir_idx + 1) % len(dirs)]

def _get_all_directions(start_dir: Direction) -> List[Direction]:
    """
    Return a list of all directions, in the right order, starting from the given
    starting direction.
    """
    dirs = [dir for dir in Direction]

    start_dir_idx = dirs.index(start_dir)

    return dirs[start_dir_idx:] + dirs[:start_dir_idx]

def _get_adj_points_dir(base_point: Point, dir: Direction) -> Set[Point]:
    """
    Get the points adjacent to base_point in the given direction.
    """
    rel_points_map = {
        Direction.NORTH: {Point(-1, -1), Point(-1,  0), Point(-1,  1)},
        Direction.SOUTH: {Point( 1, -1), Point( 1,  0), Point( 1,  1)},
        Direction.WEST:  {Point( 1, -1), Point( 0, -1), Point(-1, -1)},
        Direction.EAST:  {Point( 1,  1), Point( 0,  1), Point(-1,  1)},
    }

    return {base_point + rel_point for rel_point in rel_points_map[dir]}

def _get_adj_points(base_point: Point) -> Set[Point]:
    """
    Return all points adjacent to base_point.
    """
    return {
        point
        for dir in Direction
        for point in _get_adj_points_dir(base_point, dir)
    }

def _get_new_loc(base_point: Point, dir: Direction) -> Point:
    """
    Given the starting point base_point, move one unit in the direction dir.
    """
    move_map = {
        Direction.NORTH: Point(-1,  0),
        Direction.SOUTH: Point( 1,  0),
        Direction.EAST:  Point( 0,  1),
        Direction.WEST:  Point( 0, -1)
    }

    return base_point + move_map[dir]

def _simulate_single_step(
    elf_locations: Set[Point], start_dir: Direction
) -> Set:
    """
    Simulate a single step of the elves' ridiculous process. Return the new set
    of elf locations.
    """
    all_dirs = _get_all_directions(start_dir)

    # This maps proposed new locations to the set of locations which would move
    # to the proposed new loction.
    proposed_new_locs: Dict[Point, Set[Point]] = defaultdict(set)

    for curr_loc in elf_locations:
        # new_loc is the 'proposed location' where we think the elf will want
        # to go to.
        new_loc = curr_loc

        # We only try and move the elf if there is an adjacent elf somewhere:
        adj_points = _get_adj_points(curr_loc)
        if any(adj_point in elf_locations for adj_point in adj_points):
            # Try each direction in turn. If all directions are blocked, just
            # leave the elf where it is (I'm not sure if this is possible or
            # not).
            for dir in all_dirs:
                adj_points_dir = _get_adj_points_dir(curr_loc, dir)

                if all(
                    adj_point not in elf_locations
                    for adj_point in adj_points_dir
                ):
                    new_loc = _get_new_loc(curr_loc, dir)
                    break

        # Add the location we want to move the elf to as the proposed new
        # location.
        # This may be simply the current location if there were no adjacent
        # elves at all, or we couldn't move in any direction.
        proposed_new_locs[new_loc].add(curr_loc)

    new_elf_locations: Set[Point] = set()

    for new_loc, old_locs in proposed_new_locs.items():
        if len(old_locs) == 1:
            new_elf_locations.add(new_loc)
        else:
            assert len(old_locs) > 1
            new_elf_locations.update(old_locs)

    return new_elf_locations

def _print_elves(elf_locations: Set[Point]) -> None:
    """
    Print elf locations.
    """
    min_x = min(point.x for point in elf_locations)
    max_x = max(point.x for point in elf_locations)
    min_y = min(point.y for point in elf_locations)
    max_y = max(point.y for point in elf_locations)

    for x in range(min_x, max_x + 1):
        line_str = ""
        for y in range(min_y, max_y + 1):
            line_str += "#" if Point(x, y) in elf_locations else "."
        print(line_str)

    print("\n")


#
# Solution starts here
#
# Part 1
elf_locations = _parse_data_file(DATA_FILE)
start_dir = Direction.NORTH

for _ in range(10):
    elf_locations = _simulate_single_step(elf_locations, start_dir)
    start_dir = _get_next_direction(start_dir)

# Now get the smallest rectangle.
min_x = min(point.x for point in elf_locations)
max_x = max(point.x for point in elf_locations)
min_y = min(point.y for point in elf_locations)
max_y = max(point.y for point in elf_locations)

rectangle_area = (max_x - min_x + 1) * (max_y - min_y + 1)
print(f"Part 1, empty ground tiles: {rectangle_area - len(elf_locations)}")

# Part 2
elf_locations = _parse_data_file(DATA_FILE)
start_dir = Direction.NORTH
round_count = 1

while True:
    new_elf_locations = _simulate_single_step(elf_locations, start_dir)

    if new_elf_locations == elf_locations:
        break
    else:
        start_dir = _get_next_direction(start_dir)
        elf_locations = new_elf_locations
        round_count += 1

print(f"Part 2, number of rounds: {round_count}")
