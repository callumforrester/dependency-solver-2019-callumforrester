import itertools

from z3 import Optimize, And, Not, Or, Bool, Implies, If, Sum, BoolRef

from typing import Iterable, TypeVar, Tuple, Dict, Set, List

from src.package import Package, Command, CommandSort, PackageReference, PackageGroup
from src.expand import expand_repository, expand_commands

GUESS_STEPS = 10

UNINSTALL_COST = 1000000

BoolGroup = Dict[PackageReference, BoolRef]
BoolRepository = List[BoolGroup]


# TODO: Initial states
def encode(repository: PackageGroup,
           initial_state: Iterable[PackageReference],
           final_state_constraints: Iterable[Command],
           bools: BoolRepository) -> Optimize:

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


def total_cost(bools: BoolRepository, repository: PackageGroup) -> BoolRef:
    print('COST CONSTRAINT')
    costs = [cost(repository, from_state, to_state)
             for from_state, to_state in neighbours(bools)]
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


def constrain_delta(bools: BoolRepository) -> BoolRef:
    print('DELTA CONSTRAINT')
    deltas = [delta(from_state, to_state) <= 1
              for from_state, to_state in neighbours(bools)]
    return And(deltas)


def delta(from_state: BoolGroup, to_state: BoolGroup):
    transition = zip(from_state.values(), to_state.values())
    return Sum([If(from_bool == to_bool, 0, 1)
                for from_bool, to_bool in transition])


TNeighbour = TypeVar('TNeighbour')


def neighbours(it: Iterable[TNeighbour]) -> Iterable[
                                            Tuple[TNeighbour, TNeighbour]]:
    return zip(it, itertools.islice(it, 1, None))


def constrain_initial_state(bools: BoolGroup,
                            initial_state: Set[PackageReference]) -> BoolRef:
    return And([p == (i in initial_state) for i, p in bools.items()])


def constrain_repository(bools: BoolRepository, repository: PackageGroup) -> BoolRef:
    print('RELATIONSHIPS CONSTRAINT')
    return And([constrain_package(b, i, p)
                for b in bools for i, p in repository.items()])


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
    print('FINAL STATE CONSTRAINT')
    return And([command_to_bool(bools, c) for c in commands])


def command_to_bool(bools: BoolGroup, command: Command) -> BoolRef:
    req = next(find_bools(bools, command.reference))
    return {
        CommandSort.INSTALL: req,
        CommandSort.UNINSTALL: Not(req)
    }[command.sort]


def require_deps(bools: BoolRepository,
                 deps: Iterable[Iterable[PackageGroup]]) -> BoolRef:
    return And([require_all_ors(bools, ds) for ds in deps])


def forbid_all(bools: BoolRepository,
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


def to_bools(repository: PackageGroup,
             time_range: Iterable[int]) -> BoolRepository:
    return [{
        reference: to_bool(reference, time_step) for reference in repository
    } for time_step in time_range]


def to_bool(reference: PackageReference, time_step: int) -> Bool:
    return Bool('%s_%i' % (reference, time_step))
