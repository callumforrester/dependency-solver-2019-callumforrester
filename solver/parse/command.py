import re
from typing import List, Iterable

from solver.package.command import Command, CommandSort
from solver.parse.reference import parse_package_reference

COMMAND_REGEX = '([+-])(.*)'


def parse_command_list(commands: List[str]) -> Iterable[Command]:
    return map(parse_command, commands)


def parse_command(command: str) -> Command:
    plus_minus, reference = re.compile(COMMAND_REGEX)\
                                            .match(command)\
                                            .groups()
    return Command(CommandSort(plus_minus),
                   parse_package_reference(reference))
