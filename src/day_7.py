"""
Day 7 challenge.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import utils

DATA_FILE = "day_7.txt"

DISK_SPACE = 70000000
FREE_SPACE_NEEDED = 30000000

@dataclass
class File():
    """
    A single file.
    """
    name: str
    size: int

@dataclass
class Directory():
    """
    A single directory.
    """
    name: str
    parent_dir: Optional[Directory]
    files: List[File] = field(default_factory=list)
    child_dirs: List[Directory] = field(default_factory=list)
    size: Optional[int] = None

def _get_sub_dir(parent_dir: Directory, sub_dir_name: str) -> Directory:
    """
    Get sub dir from parent dir given the sub dir name.
    """
    sub_dirs = [
        sub_dir for sub_dir in parent_dir.child_dirs
        if sub_dir.name == sub_dir_name
    ]
    assert len(sub_dirs) == 1

    return sub_dirs.pop()

def _parse_data_file(file_name: str) -> Directory:
    """
    Parse the input file, return the root directory.
    """
    file_str = utils.read_data_file(file_name)

    current_dir: Optional[Directory] = None

    root_directory = Directory(name="", parent_dir=None)

    for line in file_str.splitlines():
        if line.startswith("$"):
            # Command: either cd or ls
            line = line[2:]
            if line.startswith("cd"):
                # This is a cd command.
                line = line[3:]
                if line == "..":
                    assert current_dir is not None
                    current_dir = current_dir.parent_dir
                elif line == "/":
                    current_dir = root_directory
                else:
                    assert current_dir is not None
                    current_dir = _get_sub_dir(current_dir, line)
            elif line.startswith("ls"):
                # About to list directory contents- no need to do anything
                pass
            else:
                assert False, "Unexpected CLI command"
        else:
            # Should be listing directory contents
            assert current_dir is not None
            if line.startswith("dir"):
                # This is a subdirectory.
                line = line[4:]
                current_dir.child_dirs.append(
                    Directory(line, parent_dir=current_dir)
                )
            else:
                # This is a file.
                size, name = line.split()
                current_dir.files.append(File(name, int(size)))

    assert current_dir is not None
    return root_directory


def _calculate_dir_size(root_dir: Directory) -> int:
    """
    Get the size of the current directory.

    This assigns the size of root_dir, and all the children dirs recursively.
    """
    dir_size = sum(child_file.size for child_file in root_dir.files)

    for child_dir in root_dir.child_dirs:
        dir_size += _calculate_dir_size(child_dir)

    root_dir.size = dir_size

    return root_dir.size

def _get_small_subdirs(
    root_dir: Directory, max_size: int = 100000
) -> List[Directory]:
    """
    Get subdirs of root_dir with at most the given size (possibly including
    root_dir).
    """
    small_subdirs: List[Directory] = []

    for sub_dir in root_dir.child_dirs:
        small_subdirs.extend(_get_small_subdirs(sub_dir))

    assert root_dir.size is not None
    if root_dir.size <= max_size:
        small_subdirs.append(root_dir)

    return small_subdirs

def _get_large_subdirs(
    root_dir: Directory, min_size: int = 100000
) -> List[Directory]:
    """
    Get subdirs of root_dir with at least the given size (possibly including
    root_dir).
    """
    large_subdirs: List[Directory] = []

    for sub_dir in root_dir.child_dirs:
        large_subdirs.extend(_get_large_subdirs(sub_dir, min_size=min_size))

    assert root_dir.size is not None
    if root_dir.size >= min_size:
        large_subdirs.append(root_dir)

    return large_subdirs

#
# Solution starts here
#
# Part 1
root_directory = _parse_data_file(DATA_FILE)

# Recursively set all directory sizes.
total_space_used = _calculate_dir_size(root_directory)

# Traverse the tree again, getting the size
small_subdirs = _get_small_subdirs(root_directory)
required_sum = sum(subdir.size for subdir in small_subdirs)

print(f"Part 1 sum: {required_sum}")

# Part 2
space_available = DISK_SPACE - total_space_used
min_delete_size = FREE_SPACE_NEEDED - space_available
assert min_delete_size > 0

large_subdirs = _get_large_subdirs(root_directory, min_size=min_delete_size)
min_dir_size = min(subdir.size for subdir in large_subdirs)

print(f"Part 2 value: {min_dir_size}")
