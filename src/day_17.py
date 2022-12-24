"""
Day 17 challenge.
"""

from __future__ import annotations

from enum import Enum
from typing import Generator, List, Set, Tuple

import utils
from utils import Point


DATA_FILE = "day_17.txt"
WIDTH = 7

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
) -> Generator[Direction, None, None]:
    """
    Return a generator which yields directions from the list `directions` in a
    loop.
    """
    while True:
        for dir in directions:
            yield dir

def shape_generator() -> Generator[Shape, None, None]:
    """
    Return a generator which yields shapes in the right order.
    """
    while True:
        for shape in Shape:
            yield shape

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
    dir_gen: Generator[Direction, None, None]
) -> Set[Point]:
    """
    Simulate a single rock with shape `shape` falling on the given start
    terrain. Return the finishing terrain.
    """
    terrain_highpoint = max(point.y for point in start_terrain)
    start_source_point = Point(2, terrain_highpoint + 4)

    rock_points = {
        start_source_point + point for point in shape.get_rock_coords()
    }

    hit_floor: bool = False

    # Keep simulating jet and a fall by one unit until we hit the floor.
    while not hit_floor:
        # Simulate the jet.
        dir = next(dir_gen)
        rock_points = _simulate_single_jet(rock_points, start_terrain, dir)

        # Simulate falling by 1.
        new_rock_points = _simulate_single_fall(rock_points, start_terrain)
        if new_rock_points == rock_points:
            hit_floor = True
        else:
            rock_points = new_rock_points

    return start_terrain | rock_points

def _adjust_terrain(terrain: Set[Point]) -> Tuple[Set[Point], int]:
    """
    Adjust the terrain to ignore points which cannot influence the simulation
    any further.
    """
    col_heights = [
        max(point.y for point in terrain if point.x == x) for x in range(WIDTH)
    ]
    min_col_height = min(col_heights)

    # Everything below min_col_height can be ignored. Shift everything above
    # min_col_height downwards.
    new_terrain: Set[Point] = set()
    for point in terrain:
        if point.y >= min_col_height:
            new_terrain.add(Point(point.x, point.y - min_col_height))

    return new_terrain, min_col_height

def _print_chamber(terrain: Set[Point]) -> None:
    """
    Print the chamber.
    """
    max_y = max(point.y for point in terrain)

    for y in range(max_y, 0, -1):
        print("|", end="")
        for x in range(WIDTH):
            if Point(x, y) in terrain:
                print("#", end="")
            else:
                print(".", end="")
        print("|")
    print("+" + "-" * WIDTH + "+\n")


#
# Solution starts here
#
directions = _parse_data_file(DATA_FILE)

# Part 1
dir_gen = direction_generator(directions)
shape_gen = shape_generator()
floor = {Point(x, 0) for x in range(WIDTH)}

# Simulate 2022 rocks falling:
terrain = floor
for _ in range(2022):
    shape = next(shape_gen)
    terrain = _simulate_single_rock(terrain, shape, dir_gen)

max_height = max(point.y for point in terrain)
print(f"Part 1, height of tower: {max_height}")

# Part 2
dir_gen = direction_generator(directions)
shape_gen = shape_generator()
floor = {Point(x, 0) for x in range(WIDTH)}

# Simulate 1000000000000 rocks falling (WTF)
terrain = floor
height_adjust_total = 0
for i in range(1000000000000):
    shape = next(shape_gen)
    terrain = _simulate_single_rock(terrain, shape, dir_gen)

    # Every so often, update the terrain so we don't have to keep track of
    # loads of point unecessarily.
    if i % 50 == 0:
        terrain, height_adjust = _adjust_terrain(terrain)
        height_adjust_total += height_adjust
    if i % 1000000000 == 0:
        print(i)

max_height = max(point.y for point in terrain) + height_adjust_total
print(f"Part 2, height of tower: {max_height}")
