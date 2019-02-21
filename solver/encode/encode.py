from dataclasses import dataclass
from z3 import Optimize, And, BoolRef
from typing import Iterable, List

from solver.package.package import PackageReference, PackageGroup
from solver.package.command import Command
from solver.encode.cost import total_cost
from solver.encode.state import EncodedState
from solver.encode.delta import at_most_one_change
from solver.encode.relationships import all_states_valid
from solver.encode.command import all_commands_obeyed
from solver.encode.install import exact_installed


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
               all_commands_obeyed(states[-1],
                                   problem.final_state_constraints),
               exact_installed(states[0], set(problem.initial_state)),
               at_most_one_change(states))
