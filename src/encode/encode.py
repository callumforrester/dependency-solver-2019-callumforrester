from z3 import Optimize, And
from typing import Iterable, List

from src.package.package import PackageReference, PackageGroup
from src.package.command import Command
from src.encode.cost import total_cost
from src.encode.state import EncodedState
from src.encode.delta import constrain_delta
from src.encode.relationships import all_states_valid
from src.encode.command import constrain_commands
from src.encode.install import exact_installed


GUESS_STEPS = 100


def encode(repository: PackageGroup,
           initial_state: Iterable[PackageReference],
           final_state_constraints: Iterable[Command],
           state: List[EncodedState]) -> Optimize:

    s = Optimize()

    formula = And(
        all_states_valid(state, repository),
        constrain_commands(state[-1], final_state_constraints),
        exact_installed(state[0], set(initial_state)),
        constrain_delta(state)
    )

    s.add(formula)
    s.minimize(total_cost(state, repository))
    return s
