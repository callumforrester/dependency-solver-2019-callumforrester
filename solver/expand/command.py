from typing import Iterable
from functools import partial

from solver.package.package import Repository
from solver.package.command import Command
from solver.expand.package import expand_reference


def expand_commands(repository: Repository,
                    commands: Iterable[Command]) -> Iterable[Command]:
    expand = partial(expand_command, repository)
    return map(expand, commands)


def expand_command(repository: Repository, command: Command) -> Command:
    command.reference = list(expand_reference(repository, command.reference))
    return command
