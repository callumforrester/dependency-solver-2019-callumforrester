import logging

from z3 import BoolRef, And, If, Sum
from typing import List, Callable

from solver.encode.state import EncodedState
from solver.neighbours import neighbours
from solver.debug import logging_tqdm


def at_most_one_change(states: List[EncodedState]) -> BoolRef:
    logging.debug('delta constraint')
    deltas = [number_of_changes(from_state, to_state) <= 1
              for from_state, to_state in logging_tqdm(neighbours(states))]
    return And(deltas)


def number_of_changes(from_state: EncodedState,
                      to_state: EncodedState) -> BoolRef:
    return sum_between_states(change, from_state, to_state)


def change(from_bool: BoolRef, to_bool: BoolRef) -> BoolRef:
    return If(from_bool == to_bool, 0, 1)


def sum_between_states(func: Callable[[BoolRef, BoolRef], BoolRef],
                       from_state: EncodedState,
                       to_state: EncodedState) -> BoolRef:
    transition = zip(from_state.values(), to_state.values())
    return Sum([func(from_bool, to_bool) for from_bool, to_bool in transition])
