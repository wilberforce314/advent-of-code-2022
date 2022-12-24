# Advent of code utilities

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


__all__ = (
    "BASE_DIR",
    "DATA_DIR",
    "get_data_file",
    "Point",
    "read_data_file",
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
