from z3 import Optimize, And
from typing import Iterable, List

from src.package.package import PackageReference, PackageGroup
from src.package.command import Command
from src.encode.cost import total_cost
from src.encode.bools import BoolGroup
from src.encode.delta import constrain_delta
from src.encode.relationships import all_states_valid
from src.encode.command import constrain_commands
from src.encode.install import exact_installed


GUESS_STEPS = 100


def encode(repository: PackageGroup,
           initial_state: Iterable[PackageReference],
           final_state_constraints: Iterable[Command],
           bools: List[BoolGroup]) -> Optimize:

    s = Optimize()

    formula = And(
        all_states_valid(bools, repository),
        constrain_commands(bools[-1], final_state_constraints),
        exact_installed(bools[0], set(initial_state)),
        constrain_delta(bools)
    )

    s.add(formula)
    s.minimize(total_cost(bools, repository))
    return s
