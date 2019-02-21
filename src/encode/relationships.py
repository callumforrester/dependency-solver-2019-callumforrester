import logging

from z3 import BoolRef, And, Implies
from typing import List, Iterable
from tqdm import tqdm

from src.encode.bools import BoolGroup
from src.package.package import Package, PackageReference, PackageGroup
from src.debug import in_debug
from src.encode.install import none_installed, require_all_ors


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
        forbid_conflicts = none_installed(bools, package.conflicts)
        conflicts = Implies(installed, forbid_conflicts)
        cst.append(conflicts)

    return And(cst)


def require_deps(bools: BoolGroup,
                 deps: Iterable[Iterable[PackageGroup]]) -> BoolRef:
    return And([require_all_ors(bools, ds) for ds in deps])
