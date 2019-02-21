from z3 import BoolRef, Not, Or
from typing import List

from src.encode.bools import BoolGroup
from src.package.package import PackageGroup


def none_installed(bools: BoolGroup,
                   constraints: List[PackageGroup]) -> BoolRef:
    return Not(require_all_ors(bools, constraints))


def require_all_ors(bools: BoolGroup,
                    constraints: List[PackageGroup]) -> BoolRef:
    return Or([any_installed(bools, c) for c in constraints])


def any_installed(bools: BoolGroup,
                  packages: PackageGroup) -> BoolRef:
    return Or(get_bools(bools, packages))


def get_bools(bools: BoolGroup, packages: PackageGroup) -> List[BoolRef]:
    return [bools[p] for p in packages]
