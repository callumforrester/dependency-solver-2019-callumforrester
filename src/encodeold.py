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


def constrain_delta(bools: List[BoolGroup]) -> BoolRef:
    logging.debug('delta constraint')
    deltas = [delta(from_state, to_state) <= 1
              for from_state, to_state in tqdm(neighbours(bools), disable=in_debug())]
    return And(deltas)


def delta(from_state: BoolGroup, to_state: BoolGroup):
    transition = zip(from_state.values(), to_state.values())
    return Sum([If(from_bool == to_bool, 0, 1)
                for from_bool, to_bool in transition])


def constrain_initial_state(bools: BoolGroup,
                            initial_state: Set[PackageReference]) -> BoolRef:
    return And([p == (i in initial_state) for i, p in bools.items()])


def constrain_repository(bools: List[BoolGroup], repository: PackageGroup) -> BoolRef:
    logging.debug('relationships constraint')
    return And([constrain_package(b, i, p)
                for i, p in tqdm(repository.items(), disable=in_debug()) for b in bools])


def constrain_package(bools: BoolGroup,
                      reference: PackageReference,
                      package: Package) -> BoolRef:
    installed = bools[reference]

    cst = []
    if package.dependencies:
        req_deps = require_deps(bools, package.dependencies)
        dependencies = Implies(installed, req_deps)
        cst.append(dependencies)

    if package.conflicts:
        forbid_conflicts = forbid_all(bools, package.conflicts)
        conflicts = Implies(installed, forbid_conflicts)
        cst.append(conflicts)

    return And(cst)


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


def require_deps(bools: BoolGroup,
                 deps: Iterable[Iterable[PackageGroup]]) -> BoolRef:
    return And([require_all_ors(bools, ds) for ds in deps])


def forbid_all(bools: BoolGroup,
               constraints: Iterable[PackageGroup]) -> BoolRef:
    return Not(require_all_ors(bools, constraints))


def require_all_ors(bools: BoolGroup,
                    constraints: Iterable[PackageGroup]) -> BoolRef:
    return Or([require_or(bools, c) for c in constraints])


def require_or(bools: BoolGroup,
               packages: PackageGroup) -> BoolRef:
    return Or(list(find_bools(bools, packages)))


def find_bools(bools: BoolGroup, packages: PackageGroup) -> Iterable[BoolRef]:
    return (bools[p] for p in packages)
