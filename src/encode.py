import itertools

from z3 import Optimize, And, Not, Or, Bool, Implies, If, Sum, BoolRef

from typing import Iterable, TypeVar, Tuple, Dict

from src.package import Package, Command, CommandSort, Constraint, \
                        PackageIdentifier
from src.expand import expand_repository, expand_commands

GUESS_STEPS = 10

BoolRepository = Dict[Dict[PackageIdentifier, int], BoolRef]


# TODO: Initial states
def encode(repository: Iterable[Package],
           final_state_constraints: Iterable[Command],
           initial_state: Iterable[Package]) -> Optimize:
    s = Optimize()

    repository = list(expand_repository(repository))
    final_state_constraints = expand_commands(repository,
                                              final_state_constraints)

    time_range = list(range(GUESS_STEPS))
    bools = to_bools(repository, time_range)

    final_time = GUESS_STEPS - 1

    for step in range(GUESS_STEPS):
        formula = And(constrain_repository(bools, repository, step),
                      constrain_commands(bools, final_state_constraints,
                                         final_time),
                      constrain_initial_state(bools, initial_state),
                      constrain_all_delta(bools, repository, time_range))
        s.add(formula)

    print(s)
    return s


def constrain_all_delta(bools: BoolRepository, repository: Iterable[Package],
                        time_steps: Iterable[int]) -> And:
    return And([constrain_delta(bools, repository, f, t)
                for f, t in neighbours(time_steps)])


TNeighbour = TypeVar('TNeighbour')


def neighbours(it: Iterable[TNeighbour]) -> Iterable[
                                            Tuple[TNeighbour, TNeighbour]]:
    return zip(it, itertools.islice(it, 1, None))


def constrain_delta(bools: BoolRepository, repository: Iterable[Package],
                    from_time: int, to_time: int) -> BoolRef:
    return Sum([delta(bools[(p.identifier, from_time)],
                      bools[(p.identifier, to_time)])
                for p in repository]) <= 1


def delta(b0: Bool, b1: Bool) -> If:
    return If(b0 == b1, 0, 1)


def constrain_initial_state(bools: BoolRepository,
                            initial_state: Iterable[Package]) -> BoolRef:
    return And([to_bool(package.identifier, 0) for package in initial_state])


def constrain_repository(bools: BoolRepository, repository: Iterable[Package],
                         at_time: int) -> BoolRef:
    return And([constrain_package(bools, p, at_time) for p in repository])


def constrain_package(bools: BoolRepository,
                      package: Package, at_time: int) -> BoolRef:
    installed = bools[(package.identifier, at_time)]

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
    return map(lambda p: bools[(p.identifier, at_time)], constraint.packages)


def to_bools(repository: Iterable[Package],
             time_range: Iterable[int]) -> BoolRepository:
    return {(p.identifier, t): to_bool(p.identifier, t)
            for p, t in itertools.product(repository, time_range)}


def to_bool(package_identifier: PackageIdentifier, time_step: int) -> Bool:
    return Bool('%s_%i' % (package_identifier.unique_name(), time_step))
