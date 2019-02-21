import logging

from z3 import BoolRef, And, Sum, If
from typing import List
from tqdm import tqdm

from solver.encode.state import EncodedState
from solver.neighbours import neighbours
from solver.debug import in_debug


def at_most_one_change(states: List[EncodedState]) -> BoolRef:
    logging.debug('delta constraint')
    deltas = [number_of_changes(from_state, to_state) <= 1
              for from_state, to_state in tqdm(neighbours(states), disable=in_debug())]
    return And(deltas)


def number_of_changes(from_state: EncodedState, to_state: EncodedState):
    transition = zip(from_state.values(), to_state.values())
    return Sum([If(from_bool == to_bool, 0, 1)
                for from_bool, to_bool in transition])
