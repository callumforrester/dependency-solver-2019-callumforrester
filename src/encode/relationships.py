import logging

from z3 import BoolRef, And, Implies
from typing import List, Optional
from tqdm import tqdm

from src.encode.bools import BoolGroup
from src.package.package import Package, PackageReference, PackageGroup
from src.debug import in_debug
from src.encode.install import none_installed, any_installed


def all_states_valid(bools: List[BoolGroup],
                     repository: PackageGroup) -> BoolRef:
    logging.debug('relationships constraint')

    constraints = [state_valid(b, i, p)
                   for i, p in tqdm(repository.items(), disable=in_debug())
                   for b in bools]
    return And(constraints)


def state_valid(bools: BoolGroup,
                reference: PackageReference,
                package: Package) -> Optional[BoolRef]:
    installed = bools[reference]
    return Implies(installed, relationships_satisfied(bools, package))


def relationships_satisfied(bools: BoolGroup, package: Package) -> BoolRef:
    return And([dependencies_satisfied(bools, package)
                if package.dependencies else True,
                conflicts_not_installed(bools, package)
                if package.conflicts else True])


def dependencies_satisfied(bools: BoolGroup, package: Package) -> BoolRef:
    return And([any_installed(bools, ds) for ds in package.dependencies])


def conflicts_not_installed(bools: BoolGroup, package: Package) -> BoolRef:
    return none_installed(bools, package.conflicts)
