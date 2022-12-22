"""
Day 15 challenge.
"""

from dataclasses import dataclass
from itertools import chain
import re
from typing import Generator, List, Set

import utils
from utils import Point

DATA_FILE = "day_15.txt"

@dataclass
class Beacon():
    """
    Class representing a beacon.
    """
    coords: Point

@dataclass
class Sensor():
    """
    Class respresenting a sensor.
    """
    coords: Point
    beacon: Beacon

    def get_distance_to_point(self, point: Point) -> int:
        """
        Return the Manhatten distance from the sensor to the given point.
        """
        return abs(self.coords.x - point.x) + abs(self.coords.y - point.y)

    def get_distance_to_beacon(self) -> int:
        """
        Return the Manhatten distance to the beacon.
        """
        return self.get_distance_to_point(self.beacon.coords)

    def is_point_closer_than_beacon(self, point: Point) -> bool:
        """
        Return True is point is as close or closer to the sensor than the
        nearest beacon to the sensor.
        """
        beacon_distance = self.get_distance_to_beacon()
        point_distance = self.get_distance_to_point(point)

        return point_distance <= beacon_distance

    def get_ruled_out_points_in_row(
        self, row: int
    ) -> Generator[Point, None, None]:
        """
        Yield points in the given row which, because of this sensor, we know
        cannot contain a beacon.
        """
        beacon_dist = self.get_distance_to_beacon()

        y_diff = abs(self.coords.y - row)
        max_x_diff = beacon_dist - y_diff

        for x_diff in range(-max_x_diff, max_x_diff + 1):
            point = Point(self.coords.x + x_diff, row)
            if point != self.beacon.coords:
                yield point

    def get_points_just_out_of_range(self) -> Generator[Point, None, None]:
        """
        Yield points which are 'just out of range'- i.e. one unit further away
        from the sensor than the beacon.
        """
        all_points: Set[Point] = set()

        distance = self.get_distance_to_beacon() + 1

        for x_diff in range(-distance, distance + 1):
            y_diff = distance - abs(x_diff)

            # Upper part
            x_coord = self.coords.x + x_diff
            y_coord = self.coords.y + y_diff
            all_points.add(Point(x_coord, y_coord))

            # Lower part
            x_coord = self.coords.x + x_diff
            y_coord = self.coords.y - y_diff
            all_points.add(Point(x_coord, y_coord))

        for point in all_points:
            yield point

def _is_point_in_grid(point: Point, grid_size: int) -> bool:
    """
    Return True if point is in the grid with corners (0,0) and
    (grid_size, grid_size), False otherwise.
    """
    return (
        0 <= point.x
        and point.x <= grid_size
        and 0 <= point.y
        and point.y <= grid_size
    )

def _is_point_not_detected(point: Point, sensors: List[Sensor]) -> bool:
    """
    Return True if point is out of the range of every sensor, False otherwise.
    """
    return not any(
        sensor.is_point_closer_than_beacon(point) for sensor in sensors
    )

def _parse_data_file(file_name: str) -> List[Sensor]:
    """
    Parse the data file into a list of sensors
    """
    sensors: List[Sensor] = []

    input_pattern = (
        r"Sensor at x=(?P<sensor_x>\-*\d+), y=(?P<sensor_y>\-*\d+): "
        r"closest beacon is at x=(?P<beacon_x>\-*\d+), y=(?P<beacon_y>\-*\d+)"
    )

    data_file_str = utils.read_data_file(file_name)

    for line in data_file_str.splitlines():
        match = re.match(input_pattern, line)
        assert match is not None

        beacon_point = Point(
            x = int(match.group("beacon_x")), y = int(match.group("beacon_y"))
        )
        sensor_point = Point(
            x = int(match.group("sensor_x")), y = int(match.group("sensor_y")),
        )

        beacon = Beacon(coords=beacon_point)
        sensor = Sensor(coords=sensor_point, beacon=beacon)

        sensors.append(sensor)

    return sensors


#
# Solution starts here
#
sensors = _parse_data_file(DATA_FILE)

# Part 1 - work out how many points in the y=2000000 row cannot contain a beacon
y_value = 2000000
no_beacon_points = {
    point
    for sensor in sensors
    for point in sensor.get_ruled_out_points_in_row(y_value)
}

print(f"Part 1: {len(no_beacon_points)} points cannot contain a beacon")

# Part 2
# I legitimately have no idea how to do this properly.
# Let's just cheat instead. Since we know there is only one location the
# distress beacon can be, look for points 'just out of range' of each sensor,
# and check whether they are out of range of every sensor.
grid_size = 4000000
found_distress_beacon = False

point_generators = [sensor.get_points_just_out_of_range() for sensor in sensors]

for point in chain(*point_generators):
    # Check if the point is out of range of every sensor.
    if (
        _is_point_in_grid(point, grid_size)
        and _is_point_not_detected(point, sensors)
    ):
        found_distress_beacon = True
        break

assert found_distress_beacon

tuning_freq = grid_size * point.x + point.y
print(f"Part 2, tuning frequency: {tuning_freq}")
