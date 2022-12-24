"""
Day 18 challenge.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Generator, List, Optional, Set

import utils

DATA_FILE = "day_18.txt"

class CubeType(Enum):
    """
    Whether a cube is interior of exterior.
    """
    INTERIOR = "interior"
    EXTERIOR = "exterior"

@dataclass(frozen=True)
class Cube():
    """
    Class representing a cube.
    """
    x: int
    y: int
    z: int

    def is_cube_adjacent(self, other_cube: Cube) -> bool:
        """
        Return True is other_cube is adjacent, False otherwise.
        """
        dist = (
            abs(self.x - other_cube.x) +
            abs(self.y - other_cube.y) +
            abs(self.z - other_cube.z)
        )

        return dist == 1

    def get_adj_cubes(self) -> Generator[Cube, None, None]:
        """
        Yield the adjacent cubes.
        """
        yield Cube(self.x - 1, self.y    , self.z)
        yield Cube(self.x + 1, self.y    , self.z)
        yield Cube(self.x,     self.y - 1, self.z)
        yield Cube(self.x    , self.y + 1, self.z)
        yield Cube(self.x    , self.y    , self.z - 1)
        yield Cube(self.x    , self.y    , self.z + 1)

    def get_exposed_surface_area(self, other_cubes: Set[Cube]) -> int:
        """
        Get the exposed surface area of the cube.
        """
        return sum(cube not in other_cubes for cube in self.get_adj_cubes())

    def get_exposed_surface_area_p2(
        self,
        droplet_cubes: Set[Cube],
        exterior_cache: Set[Cube],
        interior_cache: Set[Cube]
    ) -> int:
        """
        Get the exterior surface area of the cube for part 2.
        """
        return sum(
            1
            for cube in self.get_adj_cubes()
            if cube not in droplet_cubes
            and not _is_cube_interior(
                cube, droplet_cubes, interior_cache, exterior_cache
            )
        )

def _parse_data_file(file_name: str) -> List[Cube]:
    """
    Parse the data file into a list of cubes.
    """
    data_file_str = utils.read_data_file(file_name)

    cubes: List[Cube] = []

    for line in data_file_str.splitlines():
        x, y, z = line.split(",")
        cubes.append(Cube(int(x), int(y), int(z)))

    return cubes

def _get_exterior_cubes(droplet_cubes: Set[Cube]) -> Set[Cube]:
    """
    Get a set of cubes which are definitely exterior to the droplet.
    """
    # Pick one coordinte bigger/smaller than that of any droplet.
    # Pick average values for the other coords so that the resulting searches
    # are fairly quick.
    min_x = min(cube.x for cube in droplet_cubes) - 1
    max_x = max(cube.x for cube in droplet_cubes) + 1
    mean_x = int(sum(cube.x for cube in droplet_cubes) // len(droplet_cubes))

    min_y = min(cube.y for cube in droplet_cubes) - 1
    max_y = max(cube.y for cube in droplet_cubes) + 1
    mean_y = int(sum(cube.y for cube in droplet_cubes) // len(droplet_cubes))

    min_z = min(cube.z for cube in droplet_cubes) - 1
    max_z = max(cube.z for cube in droplet_cubes) + 1
    mean_z = int(sum(cube.z for cube in droplet_cubes) // len(droplet_cubes))

    return {
        Cube(min_x, mean_y, mean_z),
        Cube(max_x, mean_y, mean_z),
        Cube(mean_x, min_y, mean_z),
        Cube(mean_x, max_y, mean_z),
        Cube(mean_x, mean_y, min_z),
        Cube(mean_x, mean_y, max_z)
    }

def _is_cube_interior(
    cube: Cube,
    droplet_cubes: Set[Cube],
    interior_cache: Set[Cube],
    exterior_cache: Set[Cube]
) -> bool:
    """
    Work out if a cube is an interior cube. If so, update the cache of interior
    and exterior cubes.
    """
    exterior_cubes = _get_exterior_cubes(droplet_cubes)

    # Keep extending outwards until:
    # - We find that we are connected to an interior/exterior cube. If so,
    #   all connected cubes are interior/exterior.
    # - We can't find any more connected cubes (and we haven't found the
    #   exterior cube). If so, all the cubes are interior.
    # - We have realised that a connected cube is exterior. In that case, all
    #   connected cubes are exterior.
    conn_cubes = {cube}

    cube_type: Optional[CubeType] = None
    keep_looking: bool = True

    while keep_looking:
        adj_cubes = {
            new_conn_cube
            for conn_cube in conn_cubes
            for new_conn_cube in conn_cube.get_adj_cubes()
            if new_conn_cube not in droplet_cubes
        }

        # Check if any of the new cubes are in the exterior/interior cache.
        if any(cube in exterior_cache for cube in adj_cubes):
            cube_type = CubeType.EXTERIOR
            keep_looking = False
        elif any(cube in interior_cache for cube in adj_cubes):
            cube_type = CubeType.INTERIOR
            keep_looking = False

        # Check whether we discovered a guaranteed exterior cube.
        elif any(cube in exterior_cubes for cube in adj_cubes):
            cube_type = CubeType.EXTERIOR
            keep_looking = False

        # Check whether the set of connected cubes has not got any bigger. If
        # so, all cubes must be interior.
        new_conn_cubes = conn_cubes | adj_cubes
        if len(conn_cubes) == len(new_conn_cubes):
            cube_type = CubeType.INTERIOR
            keep_looking = False
        else:
            conn_cubes = new_conn_cubes

    # Update the caches.
    assert cube_type is not None
    if cube_type is CubeType.INTERIOR:
        interior_cache |= conn_cubes
    elif cube_type is CubeType.EXTERIOR:
        exterior_cache |= conn_cubes
    else:
        assert False

    return cube_type is CubeType.INTERIOR


#
# Solution starts here
#
droplet_cubes_list = _parse_data_file(DATA_FILE)

# Part 1
droplet_cubes = set(droplet_cubes_list)

total_surface_area = sum(
    cube.get_exposed_surface_area(droplet_cubes) for cube in droplet_cubes
)
print(f"Part 1: Surface area is {total_surface_area}")

# Part 2
interior_cache: Set[Cube] = set()
exterior_cache: Set[Cube] = set()

total_surface_area_p2 = sum(
    cube.get_exposed_surface_area_p2(
        droplet_cubes, exterior_cache, interior_cache
    )
    for cube in droplet_cubes
)
print(f"Part 2: Surface area is {total_surface_area_p2}")
