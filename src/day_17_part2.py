"""
Day 17 challenge - part 2 only.

Part 2 only because I am lazy and don't want to bother folding all the changes
for part 2 back into the original version.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, FrozenSet, Generator, List, Optional, Set, Tuple

import utils
from utils import Point


DATA_FILE = "day_17.txt"
WIDTH = 7
ROCK_NUM = 1000000000000

CacheEntry = Tuple[int, int, FrozenSet[Point]]

class Direction(Enum):
    """
    Enum of directions.
    """
    LEFT = "left"
    RIGHT = "right"

    @classmethod
    def get_from_char(cls, char: str) -> Direction:
        """
        Get a direction from a char.
        """
        if char == "<":
            return Direction.LEFT
        elif char == ">":
            return Direction.RIGHT
        else:
            assert False

class Shape(Enum):
    """
    Enum of rock shapes.
    """
    HOR_LINE = "-"
    PLUS = "+"
    L = "L"
    VER_LINE = "|"
    SQUARE = "sq"

    def get_rock_coords(self) -> Set[Point]:
        """
        Given a rock shape, return the relative coords making up the rock
        relative to its 'source point'

        I have defined the 'source point' to be the bottom-left point of the
        smallest rectangle containing the shape.
        """
        points: Set[Point] = set()

        if self is Shape.HOR_LINE:
            points = {Point(0, 0), Point(1, 0), Point(2, 0), Point(3, 0)}
        elif self is Shape.PLUS:
            points = {
                Point(1, 0), Point(0, 1), Point(1, 1), Point(2, 1), Point(1, 2)
            }
        elif self is Shape.L:
            points = {
                Point(0, 0), Point(1, 0), Point(2, 0), Point(2, 1), Point(2, 2)
            }
        elif self is Shape.VER_LINE:
            points = {Point(0, 0), Point(0, 1), Point(0, 2), Point(0, 3)}
        elif self is Shape.SQUARE:
            points = {Point(0, 0), Point(1, 0), Point(0, 1), Point(1, 1)}
        else:
            assert False

        return points

def _parse_data_file(file_name: str) -> List[Direction]:
    """
    Parse the data file into a list of directions.
    """
    data_file_str = utils.read_data_file(file_name)

    return [
        Direction.get_from_char(char) for char in data_file_str if char != "\n"
    ]

def direction_generator(
    directions: List[Direction]
) -> Generator[Tuple[Direction, int], None, None]:
    """
    Return a generator which yields directions from the list `directions` in a
    loop (with the index in the loop).
    """
    while True:
        for i in range(len(directions)):
            yield directions[i], i

def shape_generator() -> Generator[Tuple[Shape, int], None, None]:
    """
    Return a generator which yields shapes in the right order.
    """
    while True:
        i = 0
        for shape in Shape:
            yield shape, i
            i += 1

def _get_terrain_highpoint(terrain: Set[Point]) -> int:
    """
    Return highest y-value in terrain.
    """
    return max(point.y for point in terrain)

def _does_rock_overlap_with_terrain(
    rock_points: Set[Point], terrain: Set[Point]
) -> bool:
    """
    Return True if the rock overlaps with the terrain (including the walls),
    False otherwise.
    """
    return (
        any(rock_point in terrain for rock_point in rock_points) or
        min(point.x for point in rock_points) < 0 or
        max(point.x for point in rock_points) >= WIDTH
    )

def _simulate_single_jet(
    rock_points: Set[Point], terrain: Set[Point], dir: Direction
) -> Set[Point]:
    """
    Simuate the rock being moved by a jet of hot gas, return the set of points
    occupied by the rock after the jet.
    """
    out_points: Set[Point]

    delta = Point(-1, 0) if dir is Direction.LEFT else Point(1, 0)
    shifted_rock_points = {point + delta for point in rock_points}

    if _does_rock_overlap_with_terrain(shifted_rock_points, terrain):
        out_points = rock_points
    else:
        out_points = shifted_rock_points

    return out_points

def _simulate_single_fall(
    rock_points: Set[Point], terrain: Set[Point]
) -> Set[Point]:
    """
    Simuate the rock trying to fall by one unit (it may have hit the floor, in
    which case it doesn't move). Return the set of points occupied by the rock
    after simulating the step.
    """
    out_points: Set[Point]

    shifted_rock_points = {point + Point(0, -1) for point in rock_points}

    if _does_rock_overlap_with_terrain(shifted_rock_points, terrain):
        out_points = rock_points
    else:
        out_points = shifted_rock_points

    return out_points

def _simulate_single_rock(
    start_terrain: Set[Point],
    shape: Shape,
    dir_gen: Generator[Tuple[Direction, int], None, None]
) -> Tuple[Set[Point], int]:
    """
    Simulate a single rock with shape `shape` falling on the given start
    terrain. Return the finishing terrain and the index reached in directions.
    """
    terrain_highpoint = _get_terrain_highpoint(start_terrain)
    start_source_point = Point(2, terrain_highpoint + 4)

    rock_points = {
        start_source_point + point for point in shape.get_rock_coords()
    }

    hit_floor: bool = False

    # Keep simulating jet and a fall by one unit until we hit the floor.
    while not hit_floor:
        # Simulate the jet.
        dir, dir_idx = next(dir_gen)
        rock_points = _simulate_single_jet(rock_points, start_terrain, dir)

        # Simulate falling by 1.
        new_rock_points = _simulate_single_fall(rock_points, start_terrain)
        if new_rock_points == rock_points:
            hit_floor = True
        else:
            rock_points = new_rock_points

    return start_terrain | rock_points, dir_idx

def _print_chamber(
    terrain: Set[Point], num_of_rows: Optional[int] = None
) -> None:
    """
    Print the chamber. Optionally only print the top num_of_rows rows.
    """
    max_y = max(point.y for point in terrain)

    min_y = 0 if num_of_rows is None else max_y - num_of_rows

    for y in range(max_y, min_y, -1):
        print("|", end="")
        for x in range(WIDTH):
            if Point(x, y) in terrain:
                print("#", end="")
            else:
                print(".", end="")
        print("|")
    print("+" + "-" * WIDTH + "+\n")

def _get_cache_entry(
    shape_idx: int, dir_idx: int, terrain: Set[Point]
) -> CacheEntry:
    """
    Get a key for the cache. The key consists of:
    - The index in the list of shapes for the last rock.
    - The index in the list of directions for the last jet.
    - The top 10 layers of rocks after the last rock fell.
    """
    terrain_highpoint = _get_terrain_highpoint(terrain)

    # Get points within top 10 layers of top, return their values relative to
    # the highpoint.
    top_layers = frozenset(
        Point(point.x, point.y - terrain_highpoint + 10)
        for point in terrain
        if point.y >= terrain_highpoint - 10
    )

    return shape_idx, dir_idx, top_layers


#
# Solution starts here. The overall strategy is as follows:
# - Simulate rocks falling, cache the 'result' (i.e. what the top of the stack
#   of rocks looks like, and how many rocks were dropped) after each rock.
# - When we detect a 'cycle' (i.e. a cache entry which looks like a previous
#   entry), we have found a 'cycle'.
#   - This is not very rigorous: identical cache entries probably don't
#     guarantee that the rest of the simulation will proceed in the same way.
#     It seems to work though.
# - Work out how much the height changes in a cycle, and how many cycles we can
#   fit in total. Add the product to the total height.
# - Simulate however many more rocks we need to reach the overall total.
#
directions = _parse_data_file(DATA_FILE)

# The cache maps a cache entry (see _get_cache_entry()) to a tuple of:
# - The index of the rock that was simulated, and
# - The height of the stack after the last rock was placed.
cache: Dict[CacheEntry, Tuple[int, int]] = {}

dir_gen = direction_generator(directions)
shape_gen = shape_generator()

# The start terrain is just the floor of the chamber.
terrain = {Point(x, 0) for x in range(WIDTH)}

repeat_found: bool = False
total_height_adjust: int = 0
idx: int = 0

# Simulate rocks until we found a cycle.
while not repeat_found:
    shape, shape_idx = next(shape_gen)
    terrain, dir_idx = _simulate_single_rock(terrain, shape, dir_gen)

    cache_entry = _get_cache_entry(shape_idx, dir_idx, terrain)

    if cache_entry in cache:
        # We have found a repeat! Work out the cycle length and height change
        # in a cycle.
        cycle_length = idx - cache[cache_entry][0]
        cycle_height = _get_terrain_highpoint(terrain) - cache[cache_entry][1]
        repeat_found = True
    else:
        cache[cache_entry] = (idx, _get_terrain_highpoint(terrain))

    idx += 1

# idx gives the number of rocks simulated so far.
# cycle_length indicates how long a cycle is.
#
# The remaining number of rocks to simulate is:
# remaining = ROCK_NUM - idx - cycle_length * N, where N is the no. of cycles.
remaining_rocks = ROCK_NUM - idx
num_cycles = remaining_rocks // cycle_length
remaining_after_cycle = remaining_rocks % cycle_length

for _ in range(remaining_after_cycle):
    shape, shape_idx = next(shape_gen)
    terrain, dir_idx = _simulate_single_rock(terrain, shape, dir_gen)

# Add to the height of the stack the height that would have been gained by
# simulating the cycles.
height = _get_terrain_highpoint(terrain)
height += num_cycles * cycle_height

print(f"Part 2, height of tower: {height}")
