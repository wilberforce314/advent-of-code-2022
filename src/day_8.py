"""
Day 8 challenge.
"""

from math import prod
from typing import Iterable, List, Tuple

import utils

DATA_FILE = "day_8.txt"

def _parse_data_file(file_name: str) -> List[List[int]]:
    """
    Parse the input file into a map of trees.
    """
    height_map: List[List[int]] = []

    file_str = utils.read_data_file(file_name)

    for line in file_str.splitlines():
        height_map.append([int(num) for num in line])

    # Check tree map is rectangular.
    assert (
        min(len(row) for row in height_map) ==
        max(len(row) for row in height_map)
    )

    return height_map

def _get_view_each_direction(
    height_map: List[List[int]], row_idx: int, col_idx: int
) -> Tuple[List[int], List[int], List[int], List[int]]:
    """
    Get the view in each direction:
    - to the left
    - to the right
    - upwards
    - downwards
    """
    tree_row = height_map[row_idx]
    tree_col = [row[col_idx] for row in height_map]

    row_left = tree_row[ : col_idx]
    row_right = tree_row[(col_idx + 1) : ]
    col_above = tree_col[ : row_idx]
    col_below = tree_col[(row_idx + 1) : ]

    # Reverse row_left and col_above to get the view 'outwards' (rather than
    # 'inwards').
    row_left.reverse()
    col_above.reverse()

    return row_left, row_right, col_above, col_below

def _is_tree_visible(
    height_map: List[List[int]], row_idx: int, col_idx: int
) -> bool:
    """
    Check if the tree at (row_idx, col_idx) in height_map is visible.
    """
    tree_height = height_map[row_idx][col_idx]

    def is_visible_along_line(height: int, line_to_edge: List[int]) -> bool:
        # Check if tree is visible along given line to edge. If line to edge is
        # empty (i.e. tree is on the edge), then tree is visible!
        return (not line_to_edge or height > max(line_to_edge))

    row_left, row_right, col_above, col_below = _get_view_each_direction(
        height_map, row_idx, col_idx
    )

    tree_visible = any(
        is_visible_along_line(tree_height, line_to_edge)
        for line_to_edge in [row_left, row_right, col_above, col_below]
    )

    return tree_visible

def _get_viewing_distance(tree_height: int, view_to_edge: Iterable[int]) -> int:
    """
    Get the viewing distance along a given view.
    """
    viewing_distance = 0

    for other_height in view_to_edge:
        viewing_distance += 1
        if other_height >= tree_height:
            break

    return viewing_distance

def _get_scenic_score(
    height_map: List[List[int]], row_idx: int, col_idx: int
) -> int:
    """
    Get the scenic score for the tree at (row_idx, col_idx) in height_map.
    """
    tree_height = height_map[row_idx][col_idx]
    row_left, row_right, col_above, col_below = _get_view_each_direction(
        height_map, row_idx, col_idx
    )

    viewing_distances = [
        _get_viewing_distance(tree_height, view)
        for view in [row_left, row_right, col_above, col_below]
    ]

    return prod(viewing_distances)

#
# Solution starts here
#
height_map = _parse_data_file(DATA_FILE)

row_count = len(height_map)
col_count = len(height_map[0])

# Part 1
visible_count = sum(
    _is_tree_visible(height_map, row_idx, col_idx)
    for row_idx in range(row_count)
    for col_idx in range(col_count)
)
print(f"Part 1, number of visible trees: {visible_count}")

# Part 2
max_scenic_score = max(
    _get_scenic_score(height_map, row_idx, col_idx)
    for row_idx in range(row_count)
    for col_idx in range(col_count)
)
print(f"Part 2, best scenic score: {max_scenic_score}")
