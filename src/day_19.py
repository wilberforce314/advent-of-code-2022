"""
Day 19 challenge.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import chain, combinations
import re
from typing import Dict, List, Set

import utils


DATA_FILE = "day_19_test.txt"


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
    Adjust material_inventory for the set of materials gained in a second due
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
    assuming a new geode robot gets created every second for the remaining time
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
    robots_unavailable: Set[Material]
) -> int:
    """
    DFS algorithm for the max number of geodes obtainable.

    'Provably correct' assumptions that this recursion relies on (stolen from
    the subreddit):
    1) you only ever need to buy at most one robot in a given second.
    2) if you already are producing more ore per minute than the ore cost of the
       most expensive robot, there is no benefit to purchasing additional ore
       robots. (** NOT CURRENTLY USED **)
      - Likewise for clay and obsidian.
    3) there is no benefit to waiting a turn to buy a robot if you could buy it
       immediately. Therefore, if you choose not to buy anything, the next robot
       you buy must be one of the robots you *couldn't* already afford that turn
    4) an upper bound on the number of geodes we can hit in the time remaining
       is the current count so far, plus the number the current set of robots
       could collect in the remaining time, plus a quadratic sequence assuming
       we could optimistically build a geode robot every minute.
       - So prune the branch if that's less than the best solution found so far.

    With that in mind, the arguments are as follows:

    `blueprint` gives the blueprint in opertion.
    `time_left` gives the time left to collect rocks.
    `material_inventory` gives the materials available at this step.
    `robot_inventory` gives the robots bought and ready to collect rocks at the
                      start of this step.
    `robots_unavailable` gives the set of robots we are not allowed to buy at
                         this step. This is only non-empty if we chose not to
                         buy robots at the previous step.
    """
    global BEST_SO_FAR

    # If we have ran out of time, just return the number of geodes we currently
    # have.
    if time_left <= 0:
        BEST_SO_FAR = max(BEST_SO_FAR, material_inventory[Material.GEODE])
        return material_inventory[Material.GEODE]

    # Prune based on assumption 4) above.
    if _get_geode_num_upper_bound(
        time_left, material_inventory, robot_inventory
    ) <= BEST_SO_FAR:
        return material_inventory[Material.GEODE]

    # Work out which robots we can afford.
    affordable_robot_types = {
        robot_type
        for robot_type in Material
        if _is_robot_affordable(blueprint, material_inventory, robot_type)
    }

    results: List[int] = []

    # First get the max number of geodes after buying each possible robot type.
    for robot_type in affordable_robot_types - robots_unavailable:
        robot_costs = blueprint.robot_costs[robot_type]

        new_mat_inv = {
            req_mat: material_inventory[req_mat] - robot_costs[req_mat]
            for req_mat in Material
        }
        new_robot_inv = robot_inventory.copy()
        new_robot_inv[robot_type] += 1

        # Update the material inventory for the materials gained in this second.
        _update_material_inventory(new_mat_inv, robot_inventory)

        # All robot types are available to buy at the next iteration.
        result = _get_max_geodes(
            blueprint, time_left - 1, new_mat_inv, new_robot_inv, set()
        )
        results.append(result)

    # We may also choose not to buy any robot. Get the max number of geodes if
    # we follow this branch. Note that we list the set of robots we could have
    # bought this step as being 'not available' in the next step.
    no_buy_mat_inv = material_inventory.copy()
    no_buy_rob_inv = robot_inventory.copy()

    _update_material_inventory(no_buy_mat_inv, no_buy_rob_inv)
    result = _get_max_geodes(
        blueprint,
        time_left - 1,
        no_buy_mat_inv,
        no_buy_rob_inv,
        affordable_robot_types
    )
    results.append(result)

    return max(results)


#
# Solution starts here
#
blueprints = _parse_data_file(DATA_FILE)

# Part 1
quality_levels: List[int] = []

for blueprint in blueprints:
    # Initialize the resources available.
    material_inventory = {material: 0 for material in Material}
    robot_inventory = {material: 0 for material in Material}
    robot_inventory[Material.ORE] = 1

    # Get the max number of geodes.
    max_geode_num = _get_max_geodes(
        blueprint,
        24,
        material_inventory,
        robot_inventory,
        set()
    )

    quality_levels.append(blueprint.num * max_geode_num)

breakpoint()
print(f"Part 1: Sum of quality levels is {sum(quality_levels)}")

# Part 2
print(f"Part 2: Surface area is {None}")
