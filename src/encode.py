from z3 import Optimize, And, Not, Or, Bool, Implies

from typing import List

from src.package import Package, Repository

GUESS_STEPS = 10


def encode(packages: Repository):
    s = Optimize()

    for package, relations in packages.items():
        label = to_unique(package)
        installed = Bool(label)

        #print('AAAAA ==== ' + str(relations))
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

        if package.name == 'A':
            s.add(installed)
    return s


def to_unique(package: Package) -> str:
    return '%s_%s' % (package.name, package.version)
