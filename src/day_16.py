"""
Day 16 challenge.
"""

from math import inf, isinf
import re
from typing import Dict, FrozenSet, List, Set, Tuple

import utils

DATA_FILE = "day_16.txt"

def _parse_data_file(file_name: str) -> Tuple[
    Dict[str, int], Dict[str, Set[str]]
]:
    """
    Parse the data file into two dictionaries:
    - The first maps valve name to flow rate.
    - The second maps valve name to the set of neighbouring valves.
    """
    line_pattern = (
        r"Valve (?P<name>\S+) has flow rate=(?P<rate>\d+); tunnel[s]* lead[s]* "
        r"to valve[s]* (?P<conn_valves>.*)"
    )

    data_file_str = utils.read_data_file(file_name)

    flow_rates: Dict[str, int] = {}
    adj_valves: Dict[str, Set[str]] = {}

    for line in data_file_str.splitlines():
        match = re.match(line_pattern, line)
        assert match is not None

        valve_name = match.group("name")

        rate = int(match.group("rate"))
        flow_rates[valve_name] = rate

        adj_valves[valve_name] = {
            name.strip() for name in match.group("conn_valves").split(",")
        }

    return flow_rates, adj_valves

def _get_distances_table(
    adj_table: Dict[str, Set[str]]
) -> Dict[Tuple[str, str], int]:
    """
    Given the set of adjacent vertices in adj_table, return a dictionary giving
    the distance between each pair of vertices.

    This is just a simple application of Floyd-Wayshall.
    """
    vertices = adj_table.keys()

    # Initialize distances as infinitely large.
    out_dict = {(u, v): inf for u in vertices for v in vertices}

    # For each vertex, set the distance to each directly connected vertex to 1.
    for u in vertices:
        for v in adj_table[u]:
            out_dict[(u, v)] = 1

    # Set the distance from each vertex to itself to 0.
    for u in vertices:
        out_dict[(u, u)] = 0

    # Now for the magic Floyd-Wayshall step.
    for w in vertices:
        for u in vertices:
            for v in vertices:
                new_candidate_len = out_dict[(u, w)] + out_dict[(w, v)]
                if new_candidate_len < out_dict[(u, v)]:
                    out_dict[(u, v)] = new_candidate_len

    assert not any(isinf(out_dict[(u, v)]) for u in vertices for v in vertices)

    # Keep mypy happy
    out_dict_ints = {k: int(v) for k, v in out_dict.items()}

    return out_dict_ints

def _get_path_to_pressure_map(
    flow_rates: Dict[str, int],
    distances_dict: Dict,
    curr_valve: str,
    time_left: int,
    total_so_far: int,
    valves_activated: Tuple[str, ...],
    all_valves: Set[str]
) -> Dict[Tuple[str, ...], int]:
    """
    Helper returning dictionary mapping path traversed to total pressure
    released for each possible path in the given time over the given set of
    valves.

    When this helper is called, it assumes that:
    - We are currently at curr_valve, which has (just) been activated.
    - total_so_far includes the total payoff for all valves activated so far,
      including curr_valve.
    - valves_activated is the path traversed so far, including curr_valve.
    """
    path_to_pressure_map: Dict[Tuple[str, ...], int] = {
        valves_activated: total_so_far
    }

    possible_next_valves = all_valves - set(valves_activated)

    # If we have ran out of time, just return the single path and payoff we know
    # about, which consists of all valves activated so far.
    if time_left <= 0:
        pass

    # If we have already jumped to every node, just return the current path
    # which contains all valves. The total_so_far already includes the payoff
    # for every opened valve.
    elif not possible_next_valves:
        pass

    # Try every jump to a different valve not yet activated, include all these
    # paths in the returned set.
    else:
        other_paths: Dict[Tuple[str, ...], int] = {}

        assert possible_next_valves

        for valve in possible_next_valves:
            time_to_jump = distances_dict[(curr_valve, valve)]
            new_time_left = max(time_left - time_to_jump - 1, 0)

            valve_value = flow_rates[valve]
            valve_payoff = new_time_left * valve_value

            # Work out the total pressure released if you jump to this valve
            # and activate it.
            extra_paths = _get_path_to_pressure_map(
                flow_rates,
                distances_dict,
                curr_valve=valve,
                time_left=new_time_left,
                total_so_far=total_so_far + valve_payoff,
                valves_activated=(valves_activated + (valve,)),
                all_valves=all_valves,
            )
            other_paths.update(extra_paths)

        path_to_pressure_map.update(other_paths)

    return path_to_pressure_map

def _get_path_to_pressure_map_part1(
    flow_rates: Dict[str, int],
    distances_dict: Dict[Tuple[str, str], int],
    valves_of_interest: Set[str],
) -> Dict[Tuple[str, ...], int]:
    """
    Return a map from path taken to total pressure released for part 1.
    """
    # Call the recursive helper with the correct starting values.
    # Note that we consider "AA" to have been activated- this sets up the
    # recursive helper correctly, since then "AA" doesn't need to be considered
    # again.
    return _get_path_to_pressure_map(
        flow_rates,
        distances_dict,
        curr_valve="AA",
        time_left=30,
        total_so_far=0,
        valves_activated=("AA",),
        all_valves=valves_of_interest,
    )

def _get_path_to_pressure_map_part2(
    flow_rates: Dict[str, int],
    distances_dict: Dict[Tuple[str, str], int],
    valves_of_interest: Set[str],
) -> Dict[Tuple[str, ...], int]:
    """
    Return a map from path taken to total pressure released for part 2.
    """
    # Call the recursive helper with the correct starting values.
    # Note that we consider "AA" to have been activated- this sets up the
    # recursive helper correctly, since then "AA" doesn't need to be considered
    # again.
    return _get_path_to_pressure_map(
        flow_rates,
        distances_dict,
        curr_valve="AA",
        time_left=26,
        total_so_far=0,
        valves_activated=("AA",),
        all_valves=valves_of_interest,
    )

#
# Solution starts here
#
flow_rates, adj_dict = _parse_data_file(DATA_FILE)
distances_dict = _get_distances_table(adj_dict)

# We are only interested in walking between valves with non-zero flow rate
# (and "AA", since we start at that valve).
valves_of_interest = {
    valve for valve in flow_rates if flow_rates[valve] > 0
}
valves_of_interest.add("AA")

# Part 1
paths = _get_path_to_pressure_map_part1(
    flow_rates, distances_dict, valves_of_interest
)

max_pressure = sorted(paths.values(), reverse=True)[0]
print(f"Part 1, max pressure: {max_pressure}")

# Part 2 - The strategy here is to re-use the work from part 1 to get a mapping
#          from path to payoff, for each path within the set valves with
#          non-zero flow. We then look for the pair of disjoint paths with the
#          biggest total payoff: these are the paths that the elephant and I
#          should take.
path_map = _get_path_to_pressure_map_part2(
    flow_rates, distances_dict, valves_of_interest
)

# Consolidate paths (for a given path, all we care about is which valves were
# covered, not the order in which they were covered).
consolidated_paths: Dict[FrozenSet[str], int] = {}
for path, val in path_map.items():
    path_set = frozenset(path)

    old_val = consolidated_paths.get(path_set, 0)
    consolidated_paths[path_set] = max(old_val, val)

# Look for disjoint paths, record their payoff.
total_pressures: List[int] = []
for path1, val1 in consolidated_paths.items():
    for path2, val2 in consolidated_paths.items():
        if path1 & path2 == {"AA"}:
            total_pressures.append(val1 + val2)

print(f"Part 2, max pressure: {max(total_pressures)}")
