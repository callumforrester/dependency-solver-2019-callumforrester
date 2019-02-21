import logging

from z3 import BoolRef, And, Sum, If
from typing import List
from tqdm import tqdm

from src.encode.bools import EncodedState
from src.neighbours import neighbours
from src.debug import in_debug


def constrain_delta(bools: List[EncodedState]) -> BoolRef:
    logging.debug('delta constraint')
    deltas = [delta(from_state, to_state) <= 1
              for from_state, to_state in tqdm(neighbours(bools), disable=in_debug())]
    return And(deltas)


def delta(from_state: EncodedState, to_state: EncodedState):
    transition = zip(from_state.values(), to_state.values())
    return Sum([If(from_bool == to_bool, 0, 1)
                for from_bool, to_bool in transition])
