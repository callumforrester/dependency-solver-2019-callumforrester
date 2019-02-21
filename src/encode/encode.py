from dataclasses import dataclass
from z3 import Optimize, And, BoolRef
from typing import Iterable, List

from src.package.package import PackageReference, PackageGroup
from src.package.command import Command
from src.encode.cost import total_cost
from src.encode.state import EncodedState
from src.encode.delta import constrain_delta
from src.encode.relationships import all_states_valid
from src.encode.command import constrain_commands
from src.encode.install import exact_installed


@dataclass
class DependencyProblem:
    repository: PackageGroup
    initial_state: Iterable[PackageReference]
    final_state_constraints: Iterable[Command]


def to_z3_problem(problem: DependencyProblem,
                  states: List[EncodedState]) -> Optimize:
    return minimize(problem, states, total_cost(states, problem.repository))


def minimize(problem: DependencyProblem, states: List[EncodedState],
             to_minimize: BoolRef) -> Optimize:
    minimizer = Optimize()
    minimizer.add(to_formula(problem, states))
    minimizer.minimize(to_minimize)
    return minimizer


def to_formula(problem: DependencyProblem,
               states: List[EncodedState]) -> BoolRef:
    return And(all_states_valid(states, problem.repository),
               constrain_commands(states[-1], problem.final_state_constraints),
               exact_installed(states[0], set(problem.initial_state)),
               constrain_delta(states))
