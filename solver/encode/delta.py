import logging

from z3 import BoolRef, And, If
from typing import List
from tqdm import tqdm

from solver.encode.state import EncodedState
from solver.encode.between import sum_between_states
from solver.neighbours import neighbours
from solver.debug import in_debug


def at_most_one_change(states: List[EncodedState]) -> BoolRef:
    logging.debug('delta constraint')
    deltas = [number_of_changes(from_state, to_state) <= 1
              for from_state, to_state in tqdm(neighbours(states), disable=in_debug())]
    return And(deltas)


def number_of_changes(from_state: EncodedState,
                      to_state: EncodedState) -> BoolRef:
    return sum_between_states(change, from_state, to_state)


def change(from_bool: BoolRef, to_bool: BoolRef) -> BoolRef:
    return If(from_bool == to_bool, 0, 1)
