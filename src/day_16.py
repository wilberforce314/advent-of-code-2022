"""
Day 16 challenge.
"""

from math import inf, isinf
import re
from typing import Dict, List, Set, Tuple

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

def _get_max_pressure(
    flow_rates: Dict[str, int],
    distances_dict: Dict[Tuple[str, str], int],
) -> int:
    """
    Return the max pressure achievable.
    """
    def _get_max_pressure_internal(
        flow_rates: Dict[str, int],
        distances_dict: Dict,
        last_valve: str,
        time_left: int,
        total_so_far: int,
        valves_activated: Set[str],
        all_valves: Set[str]
    ) -> int:
        """
        Internal helper for doing the recursive step.

        When this helper is called, it assumes that:
        - We are currently at last_valve, which has (just) been activated.
        - total_so_far includes the total payoff for all valves activated so
          far, including last_valve.
        - valves_activated is the set of valves activated so far, including
          last_valve.
        """
        final_total: int

        # If we have ran out of time, just return the total accumulated so far.
        if time_left <= 0:
            final_total = total_so_far

        # If we have already jumped to every node, just return. The total_so_far
        # already includes the payoff for every opened valve.
        elif valves_activated == all_valves:
            final_total = total_so_far

        # Try every jump to a different valve not yet activated, return the best
        # total pressure.
        else:
            total_pressures: List[int] = []

            valves_to_consider = all_valves - valves_activated
            assert len(valves_to_consider) > 0

            for valve in valves_to_consider:
                time_to_jump = distances_dict[(last_valve, valve)]
                new_time_left = max(time_left - time_to_jump - 1, 0)

                valve_value = flow_rates[valve]
                valve_payoff = new_time_left * valve_value

                # Work out the total pressure released if you jump to this valve
                # and activate it.
                total_pressure = _get_max_pressure_internal(
                    flow_rates,
                    distances_dict,
                    last_valve=valve,
                    time_left=new_time_left,
                    total_so_far=total_so_far + valve_payoff,
                    valves_activated=(valves_activated | {valve}),
                    all_valves=all_valves,
                )
                total_pressures.append(total_pressure)

            final_total = max(total_pressures)

        return final_total

    # We are only interested in walking between valves with non-zero flow rate
    # (and "AA", since we start at that valve).
    valves_of_interest = {
        valve for valve in flow_rates if flow_rates[valve] > 0
    }
    valves_of_interest.add("AA")

    # Call the recursive helper with the correct starting values.
    # Note that we consider "AA" to have been activated- this sets up the
    # recursive helper correctly, since then "AA" doesn't need to be considered
    # again.
    return _get_max_pressure_internal(
        flow_rates,
        distances_dict,
        last_valve="AA",
        time_left=30,
        total_so_far=0,
        valves_activated={"AA"},
        all_valves=valves_of_interest,
    )

def _get_max_pressure_part2(
    flow_rates: Dict[str, int],
    distances_dict: Dict[Tuple[str, str], int],
) -> int:
    """
    Return the max pressure achievable for part 2.
    """
    def _get_max_pressure_internal(
        flow_rates: Dict[str, int],
        distances_dict: Dict,
        curr_valve_p1: str,
        curr_valve_p2: str,
        overall_time_left: int,
        time_left_p1: int,
        time_left_p2: int,
        total_so_far: int,
        valves_activated: Set[str],
        all_valves: Set[str]
    ) -> int:
        """
        Internal helper for doing the recursive step.

        When this helper is called, it assumes that:
        - time_left_p1 and time_left_p2 give the time until actors 1 and 2 have
          reached curr_valve_p1 and curr_valve_p2 resp, and activated it.
        - valves_activated is the set of valves activated so far, or to be
          activated if either actor has already decided to head to that valve.
        """
        final_total: int

        # If both actors are still on the way to the next valve (or activating
        # it), fast forward time.
        if time_left_p1 > 0 and time_left_p2 > 0:
            fast_forward_time = min(time_left_p1, time_left_p2)

            time_left_p1 -= fast_forward_time
            time_left_p2 -= fast_forward_time
            overall_time_left -= fast_forward_time

        # If we have ran out of time, just return the total accumulated so far.
        if overall_time_left <= 0:
            final_total = total_so_far

        # If we have already jumped to every node, just return. The total_so_far
        # already includes the payoff for every opened valve.
        elif valves_activated == all_valves:
            final_total = total_so_far

        # Figure out which actor is ready to make a new hop decision. Try every
        # jump to a different valve not yet activated, return the best total
        # pressure.
        else:
            if time_left_p1 == 0:
                curr_valve = curr_valve_p1
                moving_actor = 1
            elif time_left_p2 == 0:
                curr_valve = curr_valve_p2
                moving_actor = 2
            else:
                assert False

            total_pressures: List[int] = []

            valves_to_consider = all_valves - valves_activated
            assert len(valves_to_consider) > 0

            for valve in valves_to_consider:
                time_to_jump = distances_dict[(curr_valve, valve)]
                new_time_left = time_to_jump + 1

                valve_value = flow_rates[valve]
                valve_lifetime = max(overall_time_left - new_time_left, 0)
                valve_payoff = valve_lifetime * valve_value

                if moving_actor == 1:
                    new_curr_valve_p1 = valve
                    new_curr_valve_p2 = curr_valve_p2
                    new_time_left_p1  = new_time_left
                    new_time_left_p2  = time_left_p2
                elif moving_actor == 2:
                    new_curr_valve_p1 = curr_valve_p1
                    new_curr_valve_p2 = valve
                    new_time_left_p1  = time_left_p1
                    new_time_left_p2  = new_time_left
                else:
                    assert False

                # Work out the total pressure released if you jump to this valve
                # and activate it.
                total_pressure = _get_max_pressure_internal(
                    flow_rates,
                    distances_dict,
                    curr_valve_p1=new_curr_valve_p1,
                    curr_valve_p2=new_curr_valve_p2,
                    overall_time_left=overall_time_left,
                    time_left_p1=new_time_left_p1,
                    time_left_p2=new_time_left_p2,
                    total_so_far=total_so_far + valve_payoff,
                    valves_activated=(valves_activated | {valve}),
                    all_valves=all_valves,
                )
                total_pressures.append(total_pressure)

            final_total = max(total_pressures)

        return final_total

    # We are only interested in walking between valves with non-zero flow rate
    # (and "AA", since we start at that valve).
    valves_of_interest = {
        valve for valve in flow_rates if flow_rates[valve] > 0
    }
    valves_of_interest.add("AA")

    # Call the recursive helper with the correct starting values.
    # Note that we consider "AA" to have been activated- this sets up the
    # recursive helper correctly, since then "AA" doesn't need to be considered
    # again.
    return _get_max_pressure_internal(
        flow_rates,
        distances_dict,
        curr_valve_p1="AA",
        curr_valve_p2="AA",
        overall_time_left=26,
        time_left_p1=0,
        time_left_p2=0,
        total_so_far=0,
        valves_activated={"AA"},
        all_valves=valves_of_interest,
    )


#
# Solution starts here
#
flow_rates, adj_dict = _parse_data_file(DATA_FILE)
distances_dict = _get_distances_table(adj_dict)

# Part 1
max_pressure = _get_max_pressure(flow_rates, distances_dict)
print(f"Part 1, max pressure: {max_pressure}")

# Part 2
max_pressure_2 = _get_max_pressure_part2(flow_rates, distances_dict)
print(f"Part 2, max pressure: {max_pressure_2}")
