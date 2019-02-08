from z3 import Optimize, And, Not, Or, Bool, Implies

from typing import List

from src.package import Package, Repository, Constraints

GUESS_STEPS = 10


def encode(packages: Repository, final_state_constraints: Constraints):
    s = Optimize()

    for package, relations in packages.items():
        label = to_unique(package)
        installed = Bool(label)

        deps = And([
            Or([Bool(to_unique(dep)) for dep in dep_ands])
            for dep_ands in relations.dependencies
        ])
        s.add(Implies(installed, deps))

        conflicts = And([
            Not(Bool(to_unique(conflict)))
            for conflict in relations.conflicts
        ])
        s.add(Implies(installed, conflicts))

    for dependency in final_state_constraints.dependencies[0]: # TODO: don't use list of lists
        label = to_unique(dependency)
        s.add(Bool(label))

    for conflict in final_state_constraints.conflicts:
        label = to_unique(dependency)
        s.add(Not(Bool(label)))

    return s


def to_unique(package: Package) -> str:
    return '%s_%s' % (package.name, package.version)
