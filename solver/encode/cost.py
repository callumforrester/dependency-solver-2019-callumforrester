import logging

from z3 import BoolRef, Sum, If, And, Not
from typing import List

from solver.encode.state import EncodedState
from solver.package.package import PackageGroup
from solver.neighbours import neighbours
from solver.flatten import flatten
from solver.debug import logging_tqdm

UNINSTALL_COST = 1000000


def total_cost(states: List[EncodedState],
               repository: PackageGroup) -> BoolRef:
    logging.debug('cost constraint')
    costs = [cost(repository, from_state, to_state)
             for from_state, to_state in logging_tqdm(neighbours(states))]
    return Sum(costs)


def cost(repository: PackageGroup, from_state: EncodedState,
         to_state: EncodedState) -> BoolRef:
    transition = map(flatten, zip(from_state.items(), to_state.items()))
    return Sum([__cost(from_bool, to_bool, repository[from_package].size)
                for from_package, from_bool, _, to_bool in transition])


def __cost(from_bool: BoolRef, to_bool: BoolRef, install_cost: int) -> BoolRef:
    return If(And(Not(from_bool), to_bool), install_cost,
              If(And(from_bool, Not(to_bool)), UNINSTALL_COST, 0))
