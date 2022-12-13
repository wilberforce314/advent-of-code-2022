"""
Day 12 challenge.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Generator, List, Optional, Tuple

import utils

DATA_FILE = "day_12.txt"


class PointType(Enum):
    """
    Types of point on the map.
    """
    START = "start"
    END = "end"
    NORMAL = "normal"

@dataclass
class HillPoint():
    """
    A single point on the map.
    """
    height: int
    type: PointType = PointType.NORMAL
    steps_from_end: Optional[int] = None


def _get_height_from_letter(input_letter: str) -> int:
    """
    From a letter, get the height value.
    """
    return ord(input_letter) - ord("a")

def _parse_data_file(file_name: str) -> List[List[HillPoint]]:
    """
    Parse the data file into an array of points.
    """
    points: List[List[HillPoint]] = []

    def _get_point_from_letter(input_letter: str) -> HillPoint:
        """
        Get a hill point from the char.
        """
        if input_letter == "S":
            height_letter = "a"
            point_type = PointType.START
        elif input_letter == "E":
            height_letter = "z"
            point_type = PointType.END
        else:
            height_letter = input_letter
            point_type = PointType.NORMAL

        return HillPoint(
            height=_get_height_from_letter(height_letter), type=point_type
        )

    data_file_str = utils.read_data_file(file_name)

    points = [
        [_get_point_from_letter(letter) for letter in row]
        for row in data_file_str.splitlines()
    ]

    return points

def _get_point_from_coords(
    map: List[List[HillPoint]], coords: Tuple[int, int]
) -> HillPoint:
    """
    Return a hillpoint from its coords in map.
    """
    return map[coords[0]][coords[1]]

def _get_map_coords(
    map: List[List[HillPoint]]
) -> Generator[Tuple[int, int], None, None]:
    """
    Yield all coordinates within map.
    """
    for i in range(len(map)):
        for j in range(len(map[0])):
            yield (i, j)

def _get_start_and_end_coords(
    points: List[List[HillPoint]]
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """
    Return the coords of the start and end points.
    """
    start_points = [
        coords for coords in _get_map_coords(points)
        if _get_point_from_coords(points, coords).type is PointType.START
    ]
    assert len(start_points) == 1

    end_points = [
        coords for coords in _get_map_coords(points)
        if _get_point_from_coords(points, coords).type is PointType.END
    ]
    assert len(end_points) == 1

    return start_points[0], end_points[0]

def _get_adjacent_reachable_points(
    map: List[List[HillPoint]], centre_coords: Tuple[int, int]
) -> List[Tuple[int, int]]:
    """
    Given a point on the hill, get the set of adjacent points you can step to
    your current point.
    """
    x_coord = centre_coords[0]
    y_coord = centre_coords[1]

    # adj_points may contain points outside of map.
    adj_points = [
        (x_coord - 1, y_coord),
        (x_coord + 1, y_coord),
        (x_coord, y_coord - 1),
        (x_coord, y_coord + 1)
    ]

    num_rows = len(map)
    num_cols = len(map[0])
    end_height = map[x_coord][y_coord].height

    # Return adjacent points which are within the map and no more than 1 lower.
    return [
        point for point in adj_points
        if point[0] >= 0 and point[0] < num_rows
        and point[1] >= 0 and point[1] < num_cols and
        _get_point_from_coords(map, point).height >= end_height - 1
    ]


#
# Solution starts here
#
hill_map = _parse_data_file(DATA_FILE)

# Part 1
# Description of algorithm:
# Consider the least number of steps to the end point from each point in the
# map:
# - We can get to the end point from the end point in 0 steps.
# - Given the set of points from which we can reach the end point in n steps,
#   the set of points which are (n+1) steps from the end point is the set of
#   'adjacent' points to the previous set which we have not yet found.
#
# We measure number of steps from the end point (rather than the start point) as
# this makes part 2 easier.

start_coords, end_coords = _get_start_and_end_coords(hill_map)

start_point = _get_point_from_coords(hill_map, start_coords)
end_point = _get_point_from_coords(hill_map, end_coords)

# Set the number of steps to the end point.
end_point.steps_from_end = 0

# Set up variables for the while loop.
coords_reached_last_step: List[Tuple[int, int]] = [end_coords]
num_of_steps = 0

# Loop while we are still reaching new points.
while coords_reached_last_step:
    num_of_steps += 1
    coords_reached_this_step: List[Tuple[int, int]] = []

    # For each point reached in the previous step, check each reachable
    # adjacent point. If the adjacent point has not yet been reached, it is
    # num_of_steps steps away from the end point (i.e. in one step further away
    # than points found in the previous loop).
    for start_coords in coords_reached_last_step:
        all_adj_coords = _get_adjacent_reachable_points(hill_map, start_coords)

        for adj_coords in all_adj_coords:
            adj_point = _get_point_from_coords(hill_map, adj_coords)
            if adj_point.steps_from_end is None:
                adj_point.steps_from_end = num_of_steps
                coords_reached_this_step.append(adj_coords)

    # Update the set of coords reached in the last step for the next loop.
    coords_reached_last_step = coords_reached_this_step

print(f"Part 1, number of steps to end point: {start_point.steps_from_end}")

# Part 2
# Get the points with elevation 'a' (i.e. 0) which can reach the endpoint.
all_points = [
    _get_point_from_coords(hill_map, coords)
    for coords in _get_map_coords(hill_map)
]
low_points = [
    point for point in all_points
    if point.height == 0 and point.steps_from_end is not None
]
min_steps = min(point.steps_from_end for point in low_points)

print(f"Part 2, least number of steps to end from lowpoint: {min_steps}")
