# Advent of code utilities

from pathlib import Path


__all__ = (
    "BASE_DIR",
    "DATA_DIR",
    "get_data_file",
    "read_data_file",
)


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


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
