"""
Day 2 challenge.
"""

import dataclasses
import enum
from typing import List

import utils

DATA_FILE = "day_2.txt"

@enum.unique
class HandShape(enum.Enum):
    """
    Enum of rock-paper-scissors moves.
    """
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"

@enum.unique
class RoundResult(enum.Enum):
    """
    Result for a single round.
    """
    WIN = "win"
    DRAW = "draw"
    LOSE = "lose"

@dataclasses.dataclass
class SingleRound():
    """
    A single round of rock-paper-scissors.
    """
    opponent_move: HandShape
    my_move: HandShape

    # winning_combos is the set of (<p1 move>, <p2 move>) tuples which are
    # a win for p2.
    winning_combos = {
        (HandShape.ROCK, HandShape.PAPER),
        (HandShape.PAPER, HandShape.SCISSORS),
        (HandShape.SCISSORS, HandShape.ROCK)
    }

    @property
    def round_result(self) -> RoundResult:
        """
        The result of the round.
        """
        result: RoundResult

        if self.my_move is self.opponent_move:
            result = RoundResult.DRAW
        elif (self.opponent_move, self.my_move) in self.winning_combos:
            result = RoundResult.WIN
        else:
            result = RoundResult.LOSE

        return result

    @property
    def score(self) -> int:
        """
        Get the score for a single round.
        """
        score = 0

        # Shape score
        if self.my_move is HandShape.ROCK:
            score += 1
        elif self.my_move is HandShape.PAPER:
            score += 2
        elif self.my_move is HandShape.SCISSORS:
            score += 3

        # Round result score
        if self.round_result is RoundResult.DRAW:
            score += 3
        elif self.round_result is RoundResult.WIN:
            score += 6

        return score

    @classmethod
    def get_move_for_result(
        cls, opp_move: HandShape, desired_result: RoundResult
    ) -> HandShape:
        """
        Given an opponent move and desired result, return the move I should
        play.
        """
        my_move: HandShape

        if desired_result is RoundResult.DRAW:
            my_move = opp_move
        elif desired_result is RoundResult.WIN:
            winning_moves = {
                move for move in HandShape
                if (opp_move, move) in cls.winning_combos
            }
            my_move = winning_moves.pop()
        else:
            losing_moves = {
                move for move in HandShape
                if (move, opp_move) in cls.winning_combos
            }
            my_move = losing_moves.pop()

        return my_move

def _parse_data_file_part_1(file_name: str) -> List[SingleRound]:
    """
    Parse the data file into a 'strategy guide' (i.e. a list of rounds).
    """
    strategy_guide: List[SingleRound] = []

    opponent_decode_map = {
        "A": HandShape.ROCK, "B": HandShape.PAPER, "C": HandShape.SCISSORS
    }
    my_decode_map = {
        "X": HandShape.ROCK, "Y": HandShape.PAPER, "Z": HandShape.SCISSORS
    }

    data_file_str = utils.read_data_file(file_name)

    for line in data_file_str.splitlines():
        opponent_move, my_move = line.split()

        round = SingleRound(
            opponent_move=opponent_decode_map[opponent_move],
            my_move=my_decode_map[my_move]
        )
        strategy_guide.append(round)

    return strategy_guide

def _parse_data_file_part_2(file_name: str) -> List[SingleRound]:
    """
    Parse the data file into a 'strategy guide' (i.e. a list of rounds).
    """
    strategy_guide: List[SingleRound] = []

    opponent_decode_map = {
        "A": HandShape.ROCK, "B": HandShape.PAPER, "C": HandShape.SCISSORS
    }
    result_decode_map = {
        "X": RoundResult.LOSE, "Y": RoundResult.DRAW, "Z": RoundResult.WIN
    }

    data_file_str = utils.read_data_file(file_name)

    for line in data_file_str.splitlines():
        opp_move_str, round_res_str = line.split()

        opp_move = opponent_decode_map[opp_move_str]
        my_move = SingleRound.get_move_for_result(
            opp_move, result_decode_map[round_res_str]
        )

        strategy_guide.append(SingleRound(opp_move, my_move))

    return strategy_guide

#
# Solution starts here
#
# Part 1
strategy_guide = _parse_data_file_part_1(DATA_FILE)

total_score = sum(round.score for round in strategy_guide)
print(f"Part 1 total score: {total_score}")

# Part 2
strategy_guide = _parse_data_file_part_2(DATA_FILE)

total_score = sum(round.score for round in strategy_guide)
print(f"Part 2 total score: {total_score}")
