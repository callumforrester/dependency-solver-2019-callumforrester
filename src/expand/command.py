from typing import Iterable
from functools import partial

from src.package.package import Repository
from src.package.command import Command
from src.expand.package import expand_reference


def expand_commands(repository: Repository,
                    commands: Iterable[Command]) -> Iterable[Command]:
    expand = partial(expand_command, repository)
    return map(expand, commands)


def expand_command(repository: Repository, command: Command) -> Command:
    command.reference = expand_reference(repository, command.reference)
    return command
