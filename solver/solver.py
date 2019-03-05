from typing import Optional, List

from solver.encode.encode import DependencyProblem, to_z3_problem
from solver.package.command import Command
from solver.encode.state import generate_state_map
from solver.decode import decode

DEFAULT_TIME_STEPS = 100


def solve(problem: DependencyProblem,
          time_steps: int = DEFAULT_TIME_STEPS,
          timeout_ms: Optional[int] = None) -> Optional[List[Command]]:
    states = generate_state_map(problem.repository, range(time_steps))
    z3_problem = to_z3_problem(problem, states)
    if timeout_ms is not None:
        z3_problem.set('timeout', timeout_ms)
    if z3_problem.check():
        return decode(z3_problem.model(), states)
    else:
        return None
