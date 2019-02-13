from z3 import Optimize, And, Not, Or, Bool, Implies, Z3PPObject

from typing import Iterable, Callable, TypeVar

from src.package import Package, Command, CommandSort, PackageGroup, Constraint, PackageIdentifier
from src.expand import expand_repository, expand_commands

GUESS_STEPS = 10


# TODO: Initial states
def encode(repository: Iterable[Package],
           final_state_constraints: Iterable[Command],
           initial_state: Iterable[Package]) -> Optimize:
    s = Optimize()

    repository = list(expand_repository(repository))
    final_state_constraints = expand_commands(repository,
                                              final_state_constraints)

    for step in range(GUESS_STEPS):
        formula = And(constrain_repository(repository, step),
                      constrain_commands(final_state_constraints),
                      constrain_initial_state(initial_state))
        s.add(formula)

    print(s)
    return s


def constrain_initial_state(initial_state: Iterable[Package]) -> And:
    return And([to_bool(package.identifier, 0) for package in initial_state])


def constrain_repository(repository: Iterable[Package], at_time: int) -> And:
    return And([constrain_package(p, at_time) for p in repository])


def constrain_package(package: Package, at_time: int) -> And:
    installed = to_bool(package.identifier, at_time)

    cst = []
    if package.dependencies:
        req_deps = require_deps(package.dependencies, at_time)
        dependencies = Implies(installed, req_deps)
        cst.append(dependencies)

    if package.conflicts:
        forbid_conflicts = forbid_all(package.conflicts, at_time)
        conflicts = Implies(installed, forbid_conflicts)
        cst.append(conflicts)

    return And(cst)


def constrain_commands(commands: Iterable[Command]) -> And:
    return And([command_to_bool(c) for c in commands])


def command_to_bool(command: Command) -> Bool:
    return {
        CommandSort.INSTALL: require(command.reference, GUESS_STEPS - 1),
        CommandSort.UNINSTALL: Not(require(command.reference, GUESS_STEPS - 1))
    }[command.sort]


def require_deps(deps: Iterable[Iterable[Constraint]], at_time: int) -> And:
    return And([require_all_ors(ds, at_time) for ds in deps])


def forbid_all(constraints: Iterable[Constraint], at_time) -> Not:
    return Not(require_all_ors(constraints, at_time))


def require_all_ors(constraints: Iterable[Constraint], at_time: int) -> Or:
    return or_map(lambda c: require(c, at_time), constraints)


def require(constraint: Constraint, at_time: int) -> Or:
    return or_map(lambda p: to_bool(p.identifier, at_time), constraint.packages)


TConstraint = TypeVar('TConstraint')


def or_map(func: Callable[[TConstraint], Z3PPObject],
           constraints: Iterable[TConstraint]) -> Or:
    return Or([func(c) for c in constraints])


def to_bool(package_identifier: PackageIdentifier, time_step: int) -> Bool:
    return Bool('%s_%i' % (package_identifier.unique_name, time_step))
