from z3 import BoolRef, Not, Or, And
from typing import List, Set

from src.encode.state import EncodedState
from src.package.package import PackageGroup, PackageReference


def exact_installed(state: EncodedState,
                    installed_packages: Set[PackageReference]) -> BoolRef:
    return And([package_bool == (reference in installed_packages)
                for reference, package_bool in state.items()])


def none_installed(state: EncodedState,
                   constraints: List[PackageGroup]) -> BoolRef:
    return Not(any_installed(state, constraints))


def any_installed(state: EncodedState,
                  packages: PackageGroup) -> BoolRef:
    return Or(get_state(state, packages))


def get_state(state: EncodedState, packages: PackageGroup) -> List[BoolRef]:
    return [state[p] for p in packages]
