from z3 import BoolRef, Sum
from typing import Callable

from solver.encode.state import EncodedState


def sum_between_states(func: Callable[[BoolRef, BoolRef], BoolRef],
                       from_state: EncodedState,
                       to_state: EncodedState) -> BoolRef:
    transition = zip(from_state.values(), to_state.values())
    return Sum([func(from_bool, to_bool) for from_bool, to_bool in transition])
