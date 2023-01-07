"""
Day 22 challenge- part 2 only, I'm too lazy to fold these changes into the
original file.
"""

from __future__ import annotations

from enum import Enum
import re
from typing import Dict, List, Union, Tuple

import utils
from utils import Point


DATA_FILE = "day_22.txt"


class CellType(Enum):
    """
    Enum of cell types.
    """
    EMPTY = "empty"
    OPEN  = "open"
    WALL  = "wall"

    @classmethod
    def get_from_char(cls, char: str) -> CellType:
        """
        Get the celltype from the string representation.
        """
        if char == " ":
            cell_type = cls.EMPTY
        elif char == ".":
            cell_type = cls.OPEN
        elif char == "#":
            cell_type = cls.WALL
        else:
            assert False

        return cell_type


class Map():
    """
    Class representing a cube map.
    """
    def __init__(self, map: List[List[CellType]]) -> None:
        """
        Initialize the cube map.
        """
        self._map_arr = map
        self._face_transitions = self._get_face_transitions()

    def _get_face_transitions(self) -> Dict[
        Tuple[Point, Facing], Tuple[Point, Facing]
    ]:
        """
        Hardcoded transitions between faces (I am lazy).
        """
        face_transitions: Dict[Tuple[Point, Facing], Tuple[Point, Facing]] = {}

        for i in range(50):
            # Edge pair 1
            point_1 = Point(0, 50 + i)
            point_2 = Point(150 + i, 0)

            face_transitions[(point_1, Facing.UP)] = (point_2, Facing.RIGHT)
            face_transitions[(point_2, Facing.LEFT)] = (point_1, Facing.DOWN)

            # Edge pair 2
            point_1 = Point(0, 100 + i)
            point_2 = Point(199, i)

            face_transitions[(point_1, Facing.UP)] = (point_2, Facing.UP)
            face_transitions[(point_2, Facing.DOWN)] = (point_1, Facing.DOWN)

            # Edge pair 3
            point_1 = Point(i, 50)
            point_2 = Point(149 - i, 0)

            face_transitions[(point_1, Facing.LEFT)] = (point_2, Facing.RIGHT)
            face_transitions[(point_2, Facing.LEFT)] = (point_1, Facing.RIGHT)

            # Edge pair 4
            point_1 = Point(i, 149)
            point_2 = Point(149 - i, 99)

            face_transitions[(point_1, Facing.RIGHT)] = (point_2, Facing.LEFT)
            face_transitions[(point_2, Facing.RIGHT)] = (point_1, Facing.LEFT)

            # Edge pair 5
            point_1 = Point(49, 100 + i)
            point_2 = Point(50 + i, 99)

            face_transitions[(point_1, Facing.DOWN)] = (point_2, Facing.LEFT)
            face_transitions[(point_2, Facing.RIGHT)] = (point_1, Facing.UP)

            # Edge pair 6
            point_1 = Point(50 + i, 50)
            point_2 = Point(100, i)

            face_transitions[(point_1, Facing.LEFT)] = (point_2, Facing.DOWN)
            face_transitions[(point_2, Facing.UP)] = (point_1, Facing.RIGHT)

            # Edge pair 7
            point_1 = Point(149, 50 + i)
            point_2 = Point(150 + i, 49)

            face_transitions[(point_1, Facing.DOWN)] = (point_2, Facing.LEFT)
            face_transitions[(point_2, Facing.RIGHT)] = (point_1, Facing.UP)

        return face_transitions

    def get_cell(self, coord: Point) -> CellType:
        """
        Get a given cell in the map.
        """
        assert self.does_point_exist(coord)

        return self._map_arr[coord.x][coord.y]

    def get_row(self, row_idx: int) -> List[CellType]:
        """
        Get a row of cells in the map.
        """
        return self._map_arr[row_idx]

    def get_col(self, col_idx: int) -> List[CellType]:
        """
        Get a column of cells in the map.
        """
        return [self._map_arr[i][col_idx] for i in range(self.col_len)]

    @property
    def row_len(self) -> int:
        """
        Return the length of each row.
        """
        return len(self._map_arr[0])

    @property
    def col_len(self) -> int:
        """
        Return the length of each column.
        """
        return len(self._map_arr)

    def does_point_exist(self, point: Point) -> bool:
        """
        Return True if the point appears anywhere in the grid (including as an
        empty/unreachable cell), False otherwise.
        """
        return (
            0 <= point.x and point.x < self.col_len
            and 0 <= point.y and point.y < self.row_len
        )

    def get_row_start_and_end(self, row_idx: int) -> Tuple[Point, Point]:
        """
        Get the start and end of the points of a row that are in the map.
        """
        row = self.get_row(row_idx)

        in_map_points = [
            Point(row_idx, j)
            for j in range(self.row_len)
            if row[j] is not CellType.EMPTY
        ]

        return in_map_points[0], in_map_points[-1]

    def get_col_start_and_end(self, col_idx: int) -> Tuple[Point, Point]:
        """
        Get the start and end of the points of a column that are in the map.
        """
        col = self.get_col(col_idx)

        in_map_points = [
            Point(i, col_idx)
            for i in range(self.col_len)
            if col[i] is not CellType.EMPTY
        ]

        return in_map_points[0], in_map_points[-1]

    def get_start_pos(self) -> Tuple[Point, Facing]:
        """
        Return the start cell (0-indexed!) and facing.
        """
        row_start, _ = self.get_row_start_and_end(0)

        return row_start, Facing.RIGHT

    def get_next_pos(
        self, curr_pos: Point, facing: Facing
    ) -> Tuple[Point, Facing]:
        """
        Get the next position if we continue to travel with the current
        position/facing.

        This includes the logic for 'wrapping around' the edges of the map to
        the correct side of the cube, but not for stopping if we hit a wall. So
        the returned position may be a wall.
        """
        assert self.get_cell(curr_pos) is not CellType.EMPTY

        incr_map = {
            Facing.DOWN:  Point(1 , 0 ),
            Facing.RIGHT: Point(0 , 1 ),
            Facing.LEFT:  Point(0 , -1),
            Facing.UP:    Point(-1, 0 ),
        }

        # Try to just move along one square in a straight line.
        new_pos = curr_pos + incr_map[facing]
        new_facing = facing

        # If we exited the map, we have to wrap around to a different square on
        # the cube. Work out which!
        if (
            not self.does_point_exist(new_pos)
            or self.get_cell(new_pos) is CellType.EMPTY
        ):
            assert (curr_pos, facing) in self._face_transitions
            new_pos, new_facing = self._face_transitions[(curr_pos, facing)]

        return new_pos, new_facing


class Direction(Enum):
    """
    Enum of directions.
    """
    LEFT  = "left"
    RIGHT = "right"

    @classmethod
    def get_from_char(cls, char: str) -> Direction:
        """
        Get the celltype from the string representation.
        """
        if char == "L":
            dir = cls.LEFT
        elif char == "R":
            dir = cls.RIGHT
        else:
            assert False

        return dir

# A PathInstruct is either an int (i.e. an instruction to move forward a number
# of steps) or a Direction (an instruction to turn in a certain direction).
PathInstruct = Union[Direction, int]


class Facing(Enum):
    """
    Enum of facings.
    """
    UP    = "up"
    RIGHT = "right"
    DOWN  = "down"
    LEFT  = "left"

    @classmethod
    def get_new_facing(
        cls, curr_facing: Facing, direction: Direction
    ) -> Facing:
        """
        Get the new facing after changing direction.
        """
        facings_clockwise = [cls.UP, cls.RIGHT, cls.DOWN, cls.LEFT]

        curr_facing_idx = facings_clockwise.index(curr_facing)

        idx_incr = 1 if direction is Direction.RIGHT else -1
        new_facing_idx = (curr_facing_idx + idx_incr) % len(facings_clockwise)

        return facings_clockwise[new_facing_idx]

    def get_value(self) -> int:
        """
        Get the facing value.
        """
        value_map = {
            Facing.RIGHT: 0,
            Facing.DOWN:  1,
            Facing.LEFT:  2,
            Facing.UP:    3,
        }

        return value_map[self]


def _parse_data_file(file_name: str) -> Tuple[Map, List[PathInstruct]]:
    """
    Parse the data file into a list of monkeys.
    """
    data_file_str = utils.read_data_file(file_name)

    map: List[List[CellType]] = []
    directions: List[PathInstruct] = []

    for line in data_file_str.splitlines():
        # Ignore blank lines.
        if line == "":
            continue

        # This is a line of the map.
        if set(line).issubset({".", "#", " "}):
            new_row = [CellType.get_from_char(char) for char in line]
            map.append(new_row)
        # This should be the line of directions.
        else:
            parsing_match = re.findall(r"[LR]|[0-9]+", line)
            assert parsing_match

            for match_str in parsing_match:
                try:
                    directions.append(int(match_str))
                except ValueError:
                    directions.append(Direction.get_from_char(match_str))

    assert directions

    # Pad the rows of the map so that each row has the same length.
    row_len = max(len(row) for row in map)
    for row in map:
        curr_row_len = len(row)
        row += [CellType.EMPTY for _ in range(row_len - curr_row_len)]

    return Map(map), directions

def _simulate_path(
    map: Map, directions: List[PathInstruct]
) -> Tuple[Point, Facing]:
    """
    Simulate walking the path given by directions, return the final position
    and facing.
    """
    pos, facing = map.get_start_pos()

    for direction in directions:
        # If we are processing a direction change, update the facing.
        if isinstance(direction, Direction):
            facing = Facing.get_new_facing(facing, direction)

        # Otherwise, walk forward the given number of steps, stopping when we
        # perform the given number of steps or if we hit a wall.
        else:
            assert isinstance(direction, int)

            for _ in range(direction):
                next_pos, new_facing = map.get_next_pos(pos, facing)

                if map.get_cell(next_pos) is CellType.WALL:
                    break
                else:
                    pos = next_pos
                    facing = new_facing

    return pos, facing


#
# Solution starts here
#
map, directions = _parse_data_file(DATA_FILE)

# Part 1
final_pos, final_facing = _simulate_path(map, directions)

# Update the final coords for the horrible 1-indexing used by the problem.
final_pos += Point(1, 1)

part2_val = (1000 * final_pos.x) + (4 * final_pos.y) + final_facing.get_value()
print(f"Part 2: {part2_val}")
