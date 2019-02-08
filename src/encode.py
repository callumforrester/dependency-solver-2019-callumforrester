import z3

from typing import List

from src.package import Package, Repository

GUESS_STEPS = 10


def encode(packages: Repository):
    s = z3.Optimize()

    for package in packages.values():
        label = to_unique(package)
        installed = z3.Bool(label)

        # s.add(installed)
        deps = z3.And([
            z3.Or([
                z3.Bool(to_unique(dep)) for dep in dep_ands
            ]) for dep_ands in package.dependencies
        ])

        conflicts = z3.And([
            z3.Not(z3.Bool(to_unique(conflict)))
            for conflict in package.conflicts
        ])

        s.add(z3.Implies(installed, deps))
        s.add(z3.Implies(installed, conflicts))

        if package.name == 'A':
            s.add(installed)
        else:
            s.add(z3.Or(installed, z3.Not(installed)))
    return s


def to_unique(package: Package) -> str:
    return '%s_%s' % (package.name, package.version)
