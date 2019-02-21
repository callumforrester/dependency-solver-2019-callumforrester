import logging

from z3 import BoolRef, Sum, If, And, Not
from tqdm import tqdm
from typing import List

from solver.encode.state import EncodedState
from solver.package.package import PackageGroup
from solver.neighbours import neighbours
from solver.flatten import flatten
from solver.debug import in_debug

UNINSTALL_COST = 1000000


def total_cost(states: List[EncodedState], repository: PackageGroup) -> BoolRef:
    logging.debug('cost constraint')
    costs = [cost(repository, from_state, to_state)
             for from_state, to_state in tqdm(neighbours(states), disable=in_debug())]
    return Sum(costs)


def cost(repository: PackageGroup, from_state: EncodedState, to_state: EncodedState) -> BoolRef:
    return Sum([cst(repository, s)
                for s in zip(from_state.items(), to_state.items())])


def cst(repository, states):
    from_state, to_state = states
    from_package, from_bool = from_state
    to_package, to_bool = to_state
    uninstall_cost = UNINSTALL_COST
    install_cost = repository[from_package].size
    return If(And(Not(from_bool), to_bool), install_cost, If(And(from_bool, Not(to_bool)), uninstall_cost, 0))
