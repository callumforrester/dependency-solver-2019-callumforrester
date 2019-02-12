from z3 import Optimize, And, Not, Or, Bool, Implies, Int

from typing import Iterable, Dict, List
from functools import reduce, partial
from bisect import insort

from src.package import Package, Command, Version, PackageReference

GUESS_STEPS = 10


def expand_reference(repository: Iterable[Package],
                     reference: PackageReference) -> Iterable[Package]:
    return list(filter(lambda p: p.name == reference.name and (reference.compare(p.version, reference.version) if reference.compare else True), repository))


def encode(repository: Iterable[Package], final_state_constraints: Iterable[Command]):
    s = Optimize()

    expand = partial(expand_reference, repository)

    for package in repository:
        lbl = to_unique(package)
        installed = Bool(lbl)

        if package.dependencies:
            expanded_deps = map(lambda dor: map(expand, dor), package.dependencies)
            req_deps = require_deps(expanded_deps)
            s.add(Implies(installed, req_deps))

        if package.conflicts:
            expanded_conflicts = list(map(expand, package.conflicts))
            forbid_conflicts = forbid_all(expanded_conflicts)
            s.add(Implies(installed, forbid_conflicts))

    for constraint in final_state_constraints:
        expanded_ref = expand(constraint.reference)

        if constraint.plus_minus is '+':
            s.add(require(expanded_ref))
        elif constraint.plus_minus is '-':
            s.add(forbid(expanded_ref))

    print(s)
    return s


def require_deps(deps: Iterable[Iterable[Iterable[Package]]]):
    return And([require_all_ors(ds) for ds in deps])


def require_all_ors(packages: Iterable[Iterable[Package]]):
    return Or([require(ps) for ps in packages])


def require(packages: Iterable[Package]):
    return Or([Bool(to_unique(p)) for p in packages])


def forbid_all(packages: Iterable[Iterable[Package]]):
    return And([forbid(ps) for ps in packages])


def forbid(packages: Iterable[Package]):
    return And([Not(Bool(to_unique(p))) for p in packages])


def to_unique(package: Package) -> str:
    return '%s_%s' % (package.name, package.version)
