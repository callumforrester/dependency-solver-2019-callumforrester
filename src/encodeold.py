import itertools
import logging

from tqdm import tqdm
from z3 import Optimize, And, Not, Or, Bool, Implies, If, Sum, BoolRef
from typing import Iterable, TypeVar, Tuple, Dict, Set, List

from src.package import Package, Command, CommandSort, PackageReference, PackageGroup
from src.encode.cost import total_cost
from src.neighbours import neighbours
from src.encode.bools import BoolGroup
from src.debug import in_debug
from src.encode.delta import constrain_delta
from src.encode.initial import constrain_initial_state
from src.encode.relationships import constrain_repository
from src.encode.install import find_bools


GUESS_STEPS = 100


def encode(repository: PackageGroup,
           initial_state: Iterable[PackageReference],
           final_state_constraints: Iterable[Command],
           bools: List[BoolGroup]) -> Optimize:

    s = Optimize()

    formula = And(
        constrain_repository(bools, repository),
        constrain_commands(bools[-1], final_state_constraints),
        constrain_initial_state(bools[0], set(initial_state)),
        constrain_delta(bools)
    )

    s.add(formula)
    s.minimize(total_cost(bools, repository))
    return s


def constrain_commands(bools: BoolGroup,
                       commands: Iterable[Command]) -> BoolRef:
    logging.debug('final state constraint')
    return And([command_to_bool(bools, c) for c in tqdm(commands, disable=in_debug())])


def command_to_bool(bools: BoolGroup, command: Command) -> BoolRef:
    req = next(find_bools(bools, command.reference))
    return {
        CommandSort.INSTALL: req,
        CommandSort.UNINSTALL: Not(req)
    }[command.sort]
