from z3 import Optimize, And, Not, Or, Bool, Implies

from typing import Iterable

from src.package import Package, Command, CommandSort, PackageGroup
from src.expand import expand_repository, expand_commands

GUESS_STEPS = 10


def encode(repository: Iterable[Package],
           final_state_constraints: Iterable[Command]):
    s = Optimize()

    repository = list(expand_repository(repository))
    final_state_constraints = expand_commands(repository,
                                              final_state_constraints)

    formula = And(constrain_repository(repository),
                  constrain_commands(final_state_constraints))
    s.add(formula)

    print(s)
    return s


def constrain_repository(repository: Iterable[Package]) -> And:
    return And([constrain_package(p) for p in repository])


def constrain_package(package: Package) -> And:
    installed = Bool(package.identifier.unique_name)

    cst = []
    if package.dependencies:
        req_deps = require_deps(package.dependencies)
        dependencies = Implies(installed, req_deps)
        cst.append(dependencies)

    if package.conflicts:
        forbid_conflicts = forbid_all(package.conflicts)
        conflicts = Implies(installed, forbid_conflicts)
        cst.append(conflicts)

    return And(cst)


def constrain_commands(commands: Iterable[Command]) -> And:
    return And([to_bool(c) for c in commands])


def to_bool(command: Command) -> Bool:
    return {
        CommandSort.INSTALL: require(command.reference),
        CommandSort.UNINSTALL: Not(require(command.reference))
    }[command.sort]


def require_deps(deps: Iterable[Iterable[Iterable[PackageGroup]]]):
    return And([require_all_ors(ds) for ds in deps])


def forbid_all(constraints: Iterable[Iterable[PackageGroup]]):
    return Not(require_all_ors(constraints))


def require_all_ors(constraints: Iterable[Iterable[PackageGroup]]):
    return Or([require(ps) for ps in constraints])


def require(constraints: Iterable[PackageGroup]):
    return Or([Bool(p.identifier.unique_name) for p in constraints.packages])
