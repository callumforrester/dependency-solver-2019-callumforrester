import logging

from z3 import BoolRef, Sum, If, And, Not
from tqdm import tqdm
from typing import List

from src.encode.bools import BoolGroup
from src.package import PackageGroup
from src.neighbours import neighbours
from src.debug import in_debug

UNINSTALL_COST = 1000000


def total_cost(bools: List[BoolGroup], repository: PackageGroup) -> BoolRef:
    logging.debug('cost constraint')
    costs = [cost(repository, from_state, to_state)
             for from_state, to_state in tqdm(neighbours(bools), disable=in_debug())]
    return Sum(costs)


def cost(repository, from_state, to_state):
    return Sum([cst(repository, s)
                for s in zip(from_state.items(), to_state.items())])


def cst(repository, states):
    from_state, to_state = states
    from_package, from_bool = from_state
    to_package, to_bool = to_state
    uninstall_cost = UNINSTALL_COST
    install_cost = repository[from_package].size
    return If(And(Not(from_bool), to_bool), install_cost, If(And(from_bool, Not(to_bool)), uninstall_cost, 0))
