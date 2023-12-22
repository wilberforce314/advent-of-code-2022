# Advent of code utilities

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import wraps
from pathlib import Path
import time
from typing import Any, Callable


__all__ = (
    "BASE_DIR",
    "DATA_DIR",
    "get_data_file",
    "Direction",
    "Point",
    "read_data_file",
    "runtime",
)


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


@dataclass(frozen=True)
class Point():
    """
    A single point.
    """
    x: int
    y: int

    def __add__(self, other_point: Point) -> Point:
        """
        Add coordinates pointwise.
        """
        out_x = self.x + other_point.x
        out_y = self.y + other_point.y

        return Point(out_x, out_y)


class Direction(Enum):
    """
    Enum of directions.
    """
    NORTH = "north"
    SOUTH = "south"
    WEST = "west"
    EAST = "east"


def get_data_file(file_name: str) -> Path:
    """
    Return the path for the data file corresponding to a given day.
    """
    return DATA_DIR/file_name


def read_data_file(file_name: str) -> str:
    """
    Return the data file read as a string
    """
    data_file_path = get_data_file(file_name)

    return data_file_path.read_text()

def runtime(f: Callable) -> Callable:
    """
    Decorator used to print the execution time of a function.
    """
    @wraps(f)
    def timer_wrapper(*args: Any, **kwargs: Any) -> Any:
        """
        Wrapper which calls the function and prints the execution time.
        """
        func_name = f.__name__

        start_time = time.time()
        retval = f(*args, **kwargs)
        total_time = time.time() - start_time

        print(f"Execution time of function {func_name}: {total_time}")

        return retval

    return timer_wrapper
