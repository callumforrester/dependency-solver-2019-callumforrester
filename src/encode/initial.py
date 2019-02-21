from z3 import BoolRef, And
from typing import Set

from src.encode.bools import BoolGroup
from src.package import PackageReference


def constrain_initial_state(bools: BoolGroup,
                            initial_state: Set[PackageReference]) -> BoolRef:
    return And([p == (i in initial_state) for i, p in bools.items()])
