"""
Day 19 challenge.
"""

from dataclasses import dataclass
from enum import Enum
import re
from typing import Dict, List

import utils


DATA_FILE = "day_19.txt"


class Material(Enum):
    """
    Enum of materials.
    """
    GEODE = "geode"
    OBSIDIAN = "obsidian"
    CLAY = "clay"
    ORE = "ore"


# MaterialMap is a mapping from material type to integers. Used for storing
# amounts of rocks and amounts of robots collecting each rock type.
MaterialMap = Dict[Material, int]


@dataclass(frozen=True)
class Blueprint():
    """
    Class representing a blueprint.

    robot_costs gives a mapping from each robot type to how much of each
    material is required to build it.
    """
    num: int
    robot_costs: Dict[Material, MaterialMap]


def _parse_data_file(file_name: str) -> List[Blueprint]:
    """
    Parse the data file into a list of blueprints.
    """
    data_file_str = utils.read_data_file(file_name)

    line_pattern = (
        r"Blueprint (?P<blueprint_num>\d+): "
        r"Each ore robot costs (?P<ore_robot_cost>\d+) ore. "
        r"Each clay robot costs (?P<clay_robot_cost>\d+) ore. "
        r"Each obsidian robot costs (?P<obs_robot_ore_cost>\d+) ore "
        r"and (?P<obs_robot_clay_cost>\d+) clay. "
        r"Each geode robot costs (?P<geode_robot_ore_cost>\d+) ore "
        r"and (?P<geode_robot_obs_cost>\d+) obsidian."
    )

    blueprints: List[Blueprint] = []

    for line in data_file_str.splitlines():
        match = re.match(line_pattern, line)
        assert match is not None, f"Line: '{line}' could not be parsed"

        blueprint_num = int(match.group("blueprint_num"))

        robot_costs: Dict[Material, MaterialMap] = {
            robot_material: {material: 0 for material in Material}
            for robot_material in Material
        }

        # ORE robot costs
        #################
        robot_costs[Material.ORE][Material.ORE] = int(
            match.group("ore_robot_cost")
        )

        # CLAY robot costs
        ##################
        robot_costs[Material.CLAY][Material.ORE] = int(
            match.group("clay_robot_cost")
        )

        # OBSIDIAN robot costs
        ######################
        robot_costs[Material.OBSIDIAN][Material.ORE] = int(
            match.group("obs_robot_ore_cost")
        )
        robot_costs[Material.OBSIDIAN][Material.CLAY] = int(
            match.group("obs_robot_clay_cost")
        )

        # GEODE robot costs
        ###################
        robot_costs[Material.GEODE][Material.ORE] = int(
            match.group("geode_robot_ore_cost")
        )
        robot_costs[Material.GEODE][Material.OBSIDIAN] = int(
            match.group("geode_robot_obs_cost")
        )

        # Fill in the blueprint.
        blueprints.append(Blueprint(blueprint_num, robot_costs))

    return blueprints

def _is_robot_affordable(
    blueprint: Blueprint, mat_inventory: MaterialMap, robot_type: Material
) -> bool:
    """
    True if the given robot type is affordable.
    """
    robot_costs = blueprint.robot_costs[robot_type]

    return all(
        mat_inventory[req_mat] >= robot_costs[req_mat] for req_mat in Material
    )

def _update_material_inventory(
    material_inventory: MaterialMap, robot_inventory: MaterialMap,
) -> None:
    """
    Adjust material_inventory for the set of materials gained in a minute due
    to the robots in robot_inventory.
    """
    for material in Material:
        material_inventory[material] += robot_inventory[material]

def _get_geode_num_upper_bound(
    time_left: int,
    material_inventory: MaterialMap,
    robot_inventory: MaterialMap,
) -> int:
    """
    Get an upper bound on the number of geodes which can be collected, by
    assuming a new geode robot gets created every minute for the remaining time
    left.
    """
    curr_geode_num = material_inventory[Material.GEODE]
    curr_geode_robot_num = robot_inventory[Material.GEODE]

    return (
        curr_geode_num +
        sum(range(curr_geode_robot_num, curr_geode_robot_num + time_left))
    )

# Best total geode num found so far. Used for pruning branches.
BEST_SO_FAR: int = -1

def _get_max_geodes(
    blueprint: Blueprint,
    time_left: int,
    material_inventory: MaterialMap,
    robot_inventory: MaterialMap,
    target_robot: Material,
) -> int:
    """
    DFS algorithm for the max number of geodes obtainable.

    'Provably correct' assumptions that this recursion relies on (stolen from
    the subreddit):
    1) you only ever need to buy at most one robot in a given minute.
    2) an upper bound on the number of geodes we can hit in the time remaining
       is the current count so far, plus the number the current set of robots
       could collect in the remaining time, plus a quadratic sequence assuming
       we could optimistically build a geode robot every minute.
       - so prune the branch if that's less than the best solution found so far.
    3) we never need more ore robots than the maximum number of ore needed for a
       single robot. Similarly for the clay and obsidian robots.
       - this follows from 1).

    With that in mind, the arguments are as follows:

    `blueprint`          gives the blueprint we are using.
    `time_left`          gives the time left to collect rocks.
    `material_inventory` gives the materials available at this step.
    `robot_inventory`    gives the robots bought and ready to collect rocks at
                         the start of this step.
    `target_robot`       gives the robot we will try to buy next.
    """
    global BEST_SO_FAR
    current_geode_num = material_inventory[Material.GEODE]

    # If we have ran out of time, just return the number of geodes we currently
    # have.
    if time_left <= 0:
        BEST_SO_FAR = max(BEST_SO_FAR, current_geode_num)
        return current_geode_num

    # Prune based on assumption 2) above.
    if _get_geode_num_upper_bound(
        time_left, material_inventory, robot_inventory
    ) <= BEST_SO_FAR:
        return current_geode_num

    # Prune based on 3): work out the max number of robots of type target_robot
    # we could possibly need. If we already have that many, just return.
    max_cost = max(
        blueprint.robot_costs[robot_type][target_robot]
        for robot_type in Material
    )
    if (
        target_robot is not Material.GEODE and
        robot_inventory[target_robot] >= max_cost
    ):
        return current_geode_num

    # If the target robot is affordable, buy it, and then get the max geode num
    # for each next target robot type.
    if _is_robot_affordable(blueprint, material_inventory, target_robot):
        robot_costs = blueprint.robot_costs[target_robot]

        new_mat_inv = {
            req_mat: material_inventory[req_mat] - robot_costs[req_mat]
            for req_mat in Material
        }
        new_robot_inv = robot_inventory.copy()
        new_robot_inv[target_robot] += 1

        # Update resources gained in this minute.
        _update_material_inventory(new_mat_inv, robot_inventory)

        max_geodes = max(
            _get_max_geodes(
                blueprint, time_left - 1, new_mat_inv, new_robot_inv, new_target
            )
            for new_target in Material
        )
    # If the target robot is not yet affordable, just fast forward time by 1 min
    else:
        new_mat_inv = material_inventory.copy()
        new_robot_inv = robot_inventory.copy()

        _update_material_inventory(new_mat_inv, robot_inventory)

        max_geodes = _get_max_geodes(
            blueprint, time_left - 1, new_mat_inv, new_robot_inv, target_robot
        )

    return max_geodes

@utils.runtime
def _get_max_geodes_part1(blueprint: Blueprint) -> int:
    """
    Get the max number of geodes for part 1.
    """
    global BEST_SO_FAR

    max_geode_nums: List[int] = []

    # Need to reset the 'best geode num found so far'.
    BEST_SO_FAR = -1

    for first_target in Material:
        material_inventory = {material: 0 for material in Material}
        robot_inventory = {material: 0 for material in Material}
        robot_inventory[Material.ORE] = 1

        max_geode_nums.append(
            _get_max_geodes(
                blueprint, 24, material_inventory, robot_inventory, first_target
            )
        )

    return max(max_geode_nums)

@utils.runtime
def _get_max_geodes_part2(blueprint: Blueprint) -> int:
    """
    Get the max number of geodes for part 2.
    """
    global BEST_SO_FAR

    max_geode_nums: List[int] = []

    # Need to reset the 'best geode num found so far'.
    BEST_SO_FAR = -1

    for first_target in Material:
        material_inventory = {material: 0 for material in Material}
        robot_inventory = {material: 0 for material in Material}
        robot_inventory[Material.ORE] = 1

        max_geode_nums.append(
            _get_max_geodes(
                blueprint, 32, material_inventory, robot_inventory, first_target
            )
        )

    return max(max_geode_nums)


#
# Solution starts here
#
blueprints = _parse_data_file(DATA_FILE)

# Part 1
quality_levels: List[int] = []

for blueprint in blueprints:
    # Get the max number of geodes.
    max_geode_num = _get_max_geodes_part1(blueprint)
    quality_levels.append(blueprint.num * max_geode_num)

print(f"Part 1: Sum of quality levels is {sum(quality_levels)}")

# Part 2
geode_nums_part2: List[int] = []

for blueprint in blueprints[:3]:
    geode_nums_part2.append(_get_max_geodes_part2(blueprint))

product = 1
for geode_num in geode_nums_part2:
    product *= geode_num
print(f"Part 2: product is {product}")
