"""
Day 14 challenge.
"""

from typing import List, Optional, Set

import utils
from utils import Point

DATA_FILE = "day_14.txt"


def _parse_data_file(file_name: str) -> List[List[Point]]:
    """
    Parse the data file into a list of rock paths.
    """
    data_file_str = utils.read_data_file(file_name)

    paths: List[List[Point]] = []

    for line in data_file_str.splitlines():
        rock_path: List[Point] = []
        line_tokens = [token.strip() for token in line.split("->")]

        for token in line_tokens:
            x_str, y_str = token.split(",")
            rock_path.append(Point(int(x_str), int(y_str)))

        paths.append(rock_path)

    return paths

def _get_rock_region(rock_paths: List[List[Point]]) -> Set[Point]:
    """
    Get the set of points occupied by the rocks described by rock_paths.
    """
    region: Set[Point] = set()

    def _get_points_between_endpoints(start: Point, end: Point) -> Set[Point]:
        """
        Return the set of points between two endpoints.
        """
        points: Set[Point] = set()
        if start.x == end.x:
            min_y = min(start.y, end.y)
            max_y = max(start.y, end.y)
            points = {Point(start.x, y) for y in range(min_y, max_y + 1)}
        elif start.y == end.y:
            min_x = min(start.x, end.x)
            max_x = max(start.x, end.x)
            points = {Point(x, start.y) for x in range(min_x, max_x + 1)}
        else:
            assert False

        return points

    for path in rock_paths:
        # Add all the points described by path to the overall set.
        for start, end in zip(path, path[1:]):
            region |= _get_points_between_endpoints(start, end)

    return region

def _do_single_sand_step(
    start_point: Point, occupied_points: Set[Point], floor: Optional[int] = None
) -> Point:
    """
    Simulate a single step for the sand particle.
    """
    curr_x = start_point.x
    curr_y = start_point.y

    # Check if we have hit the floor.
    if floor is not None and start_point.y >= floor - 1:
        pass
    # If not, try to go down one step.
    elif Point(curr_x, curr_y + 1) not in occupied_points:
        curr_y += 1
    # If that wasn't possible, try to got down one step to the left.
    elif Point(curr_x - 1, curr_y + 1) not in occupied_points:
        curr_x -= 1
        curr_y += 1
    # If that wasn't possible, try to got down one step to the right.
    elif Point(curr_x + 1, curr_y + 1) not in occupied_points:
        curr_x += 1
        curr_y += 1
    # There is nowhere for the sand to go, i.e. the sand is resting.
    else:
        pass

    return Point(curr_x, curr_y)

def _simulate_sand_particle_part_1(
    start_point: Point, occupied_points: Set[Point]
) -> Optional[Point]:
    """
    Simulate a sand particle starting at start_point. Return the final resting
    position of the sand particle, or None if it is lost in the void.
    """
    final_point: Optional[Point]

    lost_to_void: bool = False
    resting: bool = False
    curr_point = start_point

    while not lost_to_void and not resting:
        assert curr_point not in occupied_points

        next_point = _do_single_sand_step(curr_point, occupied_points)

        if next_point == curr_point:
            resting = True
        else:
            curr_point = next_point

        # Check if the sand has fallen past the lowest rock formation. If so,
        # it has been lost to the void.
        if next_point.y > max(point.y for point in occupied_points):
            lost_to_void = True

    if resting:
        final_point = curr_point
    else:
        assert lost_to_void
        final_point = None

    return final_point

def _simulate_sand_particle_part_2(
    start_point: Point, occupied_points: Set[Point], floor: int
) -> Optional[Point]:
    """
    Simulate a sand particle starting at start_point for part 2. Return the
    final resting position of the sand particle.
    """
    resting: bool = False
    curr_point = start_point

    while not resting:
        assert curr_point not in occupied_points

        next_point = _do_single_sand_step(curr_point, occupied_points, floor)

        if next_point == curr_point:
            resting = True
        else:
            curr_point = next_point

    return curr_point

#
# Solution starts here
#
rock_paths = _parse_data_file(DATA_FILE)
rock_region = _get_rock_region(rock_paths)

# Part 1
occupied_points = rock_region.copy()
source = Point(500, 0)

finished: bool = False
num_sand: int = 0
while not finished:
    resting_point = _simulate_sand_particle_part_1(source, occupied_points)

    if resting_point is None:
        finished = True
    else:
        num_sand += 1
        occupied_points.add(resting_point)

print(f"Part 1, number of sand units: {num_sand}")

# Part 2
occupied_points = rock_region.copy()

finished = False
num_sand = 0

floor = max(point.y for point in occupied_points) + 2

while not finished:
    resting_point = _simulate_sand_particle_part_2(
        source, occupied_points, floor=floor)

    num_sand += 1

    assert resting_point is not None
    occupied_points.add(resting_point)

    if resting_point == source:
        # The source is smothered.
        finished = True

print(f"Part 2, number of sand units: {num_sand}")
