from z3 import BoolRef, Not, Or
from typing import Iterable

from src.encode.bools import BoolGroup
from src.package.package import PackageGroup


def forbid_all(bools: BoolGroup,
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
