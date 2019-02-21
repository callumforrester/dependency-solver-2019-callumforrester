import logging

from typing import Dict, List

from solver.encode.encode import DependencyProblem
from solver.parse.package import parse_repository
from solver.parse.reference import parse_package_reference
from solver.parse.command import parse_command_list
from solver.expand.package import expand_repository
from solver.expand.command import expand_commands


def parse_problem(raw_packages: Dict, raw_initial_state: List,
                  raw_final_state_constraints: List) -> DependencyProblem:
    logging.info('PART 1 - PARSE')
    logging.info('Parsing Repository')
    unexpanded_packages = parse_repository(raw_packages)
    logging.debug('unexpanded_packages: %s', unexpanded_packages)
    logging.info('Expanding Repository')
    packages = expand_repository(unexpanded_packages)
    logging.debug('expanded_packages: %s', packages)

    # Parse constraints
    logging.info('Parsing Final State')
    unexpanded_final_state_constraints = parse_command_list(raw_final_state_constraints)
    final_state_constraints = list(expand_commands(unexpanded_packages, unexpanded_final_state_constraints))
    logging.debug('final_state_constraints: %s', final_state_constraints)

    logging.info('Parsing Initial State')
    initial_state = list(map(parse_package_reference, raw_initial_state))
    logging.debug('initial_state: %s', initial_state)
    return DependencyProblem(packages, initial_state, final_state_constraints)
