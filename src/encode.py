import itertools

from z3 import Optimize, And, Not, Or, Bool, Implies, If, Sum, BoolRef

from typing import Iterable, TypeVar, Tuple, Dict, Set

from src.package import Package, Command, CommandSort, Constraint, \
                        PackageIdentifier
from src.expand import expand_repository, expand_commands

GUESS_STEPS = 10

UNINSTALL_COST = 1000000

BoolRepository = Dict[int, Dict[PackageIdentifier, BoolRef]]


# TODO: Initial states
def encode(bools: BoolRepository,
           repository: Iterable[Package],
           final_state_constraints: Iterable[Command],
           initial_state: Iterable[PackageIdentifier],
           time_range: Iterable[int]) -> Optimize:

    s = Optimize()

    repository = list(expand_repository(repository))
    final_state_constraints = expand_commands(repository,
                                              final_state_constraints)

    # time_range = list(range(GUESS_STEPS))
    # bools = to_bools(repository, time_range)

    final_time = GUESS_STEPS - 1

    for step in range(GUESS_STEPS):
        formula = And(constrain_repository(bools, repository, step),
                      constrain_commands(bools, final_state_constraints,
                                         final_time),
                      constrain_initial_state(bools, set(initial_state)),
                      constrain_all_delta(bools, repository, time_range))
        s.add(formula)

    s.minimize(total_cost(bools, repository, time_range))
    return s


def total_cost(bools: BoolRepository, repository: Iterable[Package],
               time_steps: Iterable[int]) -> BoolRef:
    print('COST CONSTRAINT')
    return Sum([cost(bools[f][p.identifier], bools[t][p.identifier], p.size, UNINSTALL_COST)
                for p in repository
                for f, t in neighbours(time_steps)])


def constrain_all_delta(bools: BoolRepository, repository: Iterable[Package],
                        time_steps: Iterable[int]) -> BoolRef:
    print('DELTA CONSTRAINT')
    return And([constrain_delta(bools, repository, f, t)
                for f, t in neighbours(time_steps)])


TNeighbour = TypeVar('TNeighbour')


def neighbours(it: Iterable[TNeighbour]) -> Iterable[
                                            Tuple[TNeighbour, TNeighbour]]:
    return zip(it, itertools.islice(it, 1, None))


def constrain_delta(bools: BoolRepository, repository: Iterable[Package],
                    from_time: int, to_time: int) -> BoolRef:
    return Sum([delta(bools[from_time][p.identifier],
                      bools[to_time][p.identifier])
                for p in repository]) <= 1


def delta(b0: BoolRef, b1: BoolRef) -> BoolRef:
    return If(b0 == b1, 0, 1)


def cost(b0: BoolRef, b1: BoolRef, install_cost: int, uninstall_cost: int) -> BoolRef:
    return If(And(Not(b0), b1), install_cost, If(And(b0, Not(b1)), uninstall_cost, 0))


def constrain_initial_state(bools: BoolRepository,
                            initial_state: Set[PackageIdentifier]) -> BoolRef:
    initial_bools = bools[0]
    return And([initial_bools[i] == (i in initial_state) for i, p in initial_bools.items()])


def constrain_repository(bools: BoolRepository, repository: Iterable[Package],
                         at_time: int) -> BoolRef:
    print('RELATIONSHIPS CONSTRAINT')
    return And([constrain_package(bools, p, at_time) for p in repository])


def constrain_package(bools: BoolRepository,
                      package: Package, at_time: int) -> BoolRef:
    installed = bools[at_time][package.identifier]

    cst = []
    if package.dependencies:
        req_deps = require_deps(bools, package.dependencies, at_time)
        dependencies = Implies(installed, req_deps)
        cst.append(dependencies)

    if package.conflicts:
        forbid_conflicts = forbid_all(bools, package.conflicts, at_time)
        conflicts = Implies(installed, forbid_conflicts)
        cst.append(conflicts)

    return And(cst)


def constrain_commands(bools: BoolRepository,
                       commands: Iterable[Command],
                       final_time: int) -> BoolRef:
    print('FINAL STATE CONSTRAINT')
    return And([command_to_bool(bools, c, final_time) for c in commands])


def command_to_bool(bools: BoolRepository, command: Command,
                    final_time: int) -> BoolRef:
    req = require(bools, command.reference, final_time)
    return {
        CommandSort.INSTALL: req,
        CommandSort.UNINSTALL: Not(req)
    }[command.sort]


def require_deps(bools: BoolRepository,
                 deps: Iterable[Iterable[Constraint]],
                 at_time: int) -> BoolRef:
    return And([require_all_ors(bools, ds, at_time) for ds in deps])


def forbid_all(bools: BoolRepository,
               constraints: Iterable[Constraint], at_time: int) -> BoolRef:
    return Not(require_all_ors(bools, constraints, at_time))


def require_all_ors(bools: BoolRepository,
                    constraints: Iterable[Constraint],
                    at_time: int) -> BoolRef:
    return Or([require(bools, c, at_time) for c in constraints])


def require(bools: Iterable[BoolRef],
            constraint: Constraint, at_time: int) -> BoolRef:
    return Or(list(find_bools(bools, constraint, at_time)))


def find_bools(bools: BoolRepository, constraint: Constraint,
               at_time: int) -> Iterable[BoolRef]:
    return map(lambda p: bools[at_time][p.identifier], constraint.packages)


def to_bools(repository: Iterable[Package],
             time_range: Iterable[int]) -> BoolRepository:
    return {t: {p.identifier: to_bool(p.identifier, t) for p in repository}
            for t in time_range}


def to_bool(package_identifier: PackageIdentifier, time_step: int) -> Bool:
    return Bool('%s_%i' % (package_identifier, time_step))
