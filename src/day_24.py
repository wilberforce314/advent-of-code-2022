"""
Day 24 challenge.
"""

from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

import utils
from utils import Direction, Point


DATA_FILE = "day_24.txt"


@dataclass
class ValleyCell():
    """
    Class representing a single point in the initial valley.

    blizzard is None if there is no blizzard in the cell. Otherwise, it gives
    the direction the blizzard is moving in.
    """
    is_wall: bool = False
    blizzard: Optional[Direction] = None

    def __str__(self) -> str:
        """
        Fairly pointless stringification. Inverse of parsing.
        """
        if self.is_wall:
            return "#"

        # Not a wall.
        dir_to_str_map = {
            Direction.EAST : ">",
            Direction.NORTH : "^",
            Direction.WEST : "<",
            Direction.SOUTH : "v"
        }

        if self.blizzard is None:
            return "."
        else:
            return dir_to_str_map[self.blizzard]


# Type for an object representing the entire valley, including walls.
ValleyType = List[List[ValleyCell]]


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
        if char == "#":
            cell = ValleyCell(is_wall=True)
        elif char == ".":
            cell = ValleyCell(blizzard=None)
        else:
            cell = ValleyCell(blizzard=blizzard_map[char])

        row.append(cell)

    return row

def _parse_data_file(file_name: str) -> ValleyType:
    """
    Parse the data file.
    """
    data_file_str = utils.read_data_file(file_name)
    lines = data_file_str.splitlines()

    return [_parse_data_file_line(line) for line in lines]

def _get_valley_size(valley: ValleyType) -> Tuple[int, int]:
    """
    Get the size of the valley as (num_rows, num_cols).
    """
    return (len(valley), len(valley[0]))

def _get_valley_value(valley: ValleyType, coords: Point) -> ValleyCell:
    """
    Get the value of a point in the valley with coords `coords`.
    """
    return valley[coords.x][coords.y]

def _get_start_point(initial_valley: ValleyType) -> Point:
    """
    Get the coordinates of the start point.
    """
    _, num_cols = _get_valley_size(initial_valley)

    top_row_nonwall_coords = [
        Point(0, i) for i in range(num_cols)
        if not _get_valley_value(initial_valley, Point(0, i)).is_wall
    ]

    assert len(top_row_nonwall_coords) == 1
    return top_row_nonwall_coords[0]

def _get_end_point(initial_valley: ValleyType) -> Point:
    """
    Get the coordinates of the end point.
    """
    num_rows, num_cols = _get_valley_size(initial_valley)

    bottom_row_nonwall_coords = [
        Point(num_rows - 1, i) for i in range(num_cols)
        if not _get_valley_value(initial_valley, Point(num_rows - 1, i)).is_wall
    ]

    assert len(bottom_row_nonwall_coords) == 1
    return bottom_row_nonwall_coords[0]

def _convert_valley_to_blizzard_coords(valley_coords: Point) -> Point:
    """
    Convert the coords of a point in the valley to the coords a point in the
    array in which blizzards operate.
    """
    return Point(valley_coords.x - 1, valley_coords.y - 1)

def _convert_blizzard_to_valley_coords(blizzard_coords: Point) -> Point:
    """
    Convert the coords a point in the array in which blizzards operate to the
    coords of a point in the valley.
    """
    return Point(blizzard_coords.x + 1, blizzard_coords.y + 1)

def _is_cell_safe(
    initial_valley: ValleyType, coords: Point, step: int
) -> bool:
    """
    Determine if a given cell is safe at step `step`.
    """
    num_rows, num_cols = _get_valley_size(initial_valley)

    # Annoying special case for the start and end points - which are "in the
    # walls" (and are always safe):
    start_point = _get_start_point(initial_valley)
    end_point = _get_end_point(initial_valley)
    if coords in [start_point, end_point]:
        return True

    # The walls are never safe.
    value = _get_valley_value(initial_valley, coords)
    if value.is_wall:
        return False

    # Blizzards operate in an array which does not include the walls, and wrap
    # around 'pacman-style'.
    #
    # Points in that coordinate system have 'bc' in the name. Points in the
    # normal 'valley' coordinate system have 'vc' in the name.
    num_bc_rows = num_rows - 2
    num_bc_cols = num_cols - 2

    # Get the cell we are checking is safe in terms of 'blizzard array' coords.
    start_bc = _convert_valley_to_blizzard_coords(coords)

    # Keys:  Direction blizzard is travelling in
    # Value: Difference from start loc to coords of blizzard which will hit
    #        start_bc at the given step.
    dir_diff_map = {
        Direction.WEST: Point(0, step),
        Direction.EAST: Point(0, -step),
        Direction.SOUTH: Point(-step, 0),
        Direction.NORTH: Point(step, 0)
    }

    for dirn, diff in dir_diff_map.items():
        blz_bc = start_bc + diff

        # 'Normalize' the blizzard coords - i.e. wrap around.
        blz_bc = Point(blz_bc.x % num_bc_rows, blz_bc.y % num_bc_cols)

        # Convert back to valley coords.
        blz_vc = _convert_blizzard_to_valley_coords(blz_bc)

        blz_cell = _get_valley_value(initial_valley, blz_vc)
        assert not blz_cell.is_wall

        if blz_cell.blizzard is dirn:
            return False

    return True

def _get_safe_cells(initial_valley: ValleyType, step: int) -> Set[Point]:
    """
    Get the set of safe cells at step `step`.
    """
    num_rows, num_cols = _get_valley_size(initial_valley)

    return {
        Point(row, col)
        for row in range(num_rows)
        for col in range(num_cols)
        if _is_cell_safe(initial_valley, Point(row, col), step)
    }

def _is_point_in_bounds(valley: ValleyType, coords: Point) -> bool:
    """
    Check if the point given by `coords` is within the bounds of the valley
    (including walls).
    """
    num_rows, num_cols = _get_valley_size(valley)

    if coords.x < 0 or coords.x >= num_rows:
        return False
    if coords.y < 0 or coords.y >= num_cols:
        return False

    return True

def _get_non_wall_neighbors(valley: ValleyType, coords: Point) -> Set[Point]:
    """
    Get the points neighboring point `coords` which are not walls.
    """
    steps = {Point(0, 1), Point(0, -1), Point(1, 0), Point(-1, 0)}

    return {
        coords + step
        for step in steps
        if _is_point_in_bounds(valley, coords + step)
        and not _get_valley_value(valley, coords + step).is_wall
    }

def _add_neighboring_points(
    initial_valley: ValleyType, current_reachable_points: Set[Point]
) -> Set[Point]:
    """
    Get a set of points, return a new set including the neighbors in the valley
    which are not walls (i.e. anyway we can move to in a step).
    """
    # We can 'wait', so the current set of points are still reachable.
    new_reachable_points: Set[Point] = current_reachable_points.copy()

    # For each point, also add the neighbors.
    for point in current_reachable_points:
        new_reachable_points |= _get_non_wall_neighbors(initial_valley, point)

    return new_reachable_points

def _calculate_journey_steps(
    initial_valley: ValleyType,
    start: Point,
    end: Point,
    time_passed_at_start: int = 0
) -> int:
    """
    Work out the minimum number of steps to go from start to end.

    If the valley is not in its initial state, `time_passed_at_start` should
    be set to the number of timesteps since the valley was in its initial state.
    """
    journey_steps: int = 0
    done: bool = False

    # Only the start point is reachable after 0 steps.
    reachable_cells = {start}

    while not done:
        journey_steps += 1
        print(f"Journey step: {journey_steps}")
        safe_cells = _get_safe_cells(
            initial_valley, journey_steps + time_passed_at_start
        )

        tmp_reachable_cells = _add_neighboring_points(
            initial_valley, reachable_cells
        )
        reachable_cells = tmp_reachable_cells & safe_cells

        if end in reachable_cells:
            done = True

    return journey_steps

#
# Solution starts here
#
# Part 1
initial_valley = _parse_data_file(DATA_FILE)
start_point = _get_start_point(initial_valley)
end_point = _get_end_point(initial_valley)

part1_steps = _calculate_journey_steps(
    initial_valley, start=start_point, end=end_point
)
print(f"Part 1: Done in {part1_steps} steps")

# Part 2
part2_steps_back = _calculate_journey_steps(
    initial_valley,
    start=end_point,
    end=start_point,
    time_passed_at_start=part1_steps
)

part2_steps_forward = _calculate_journey_steps(
    initial_valley,
    start=start_point,
    end=end_point,
    time_passed_at_start=part1_steps + part2_steps_back
)

print("Part2 solutions: ")
print(f"  Steps there: {part1_steps}")
print(f"  Steps back: {part2_steps_back}")
print(f"  Steps there again: {part2_steps_forward}")
print(f"  Total: {part1_steps + part2_steps_back + part2_steps_forward}")
