from typing import Iterable
from functools import partial

from src.package import Package, Command, PackageReference, PackageGroup


def expand_commands(repository: Iterable[Package],
                    commands: Iterable[Command]) -> Iterable[Command]:
    expand = partial(expand_command, repository)
    return map(expand, commands)


def expand_command(repository: Iterable[Package], command: Command) -> Command:
    command.reference = expand_reference(repository, command.reference)
    return command


def expand_repository(repository: Iterable[Package]) -> Iterable[Package]:
    expand = partial(expand_package, repository)
    return map(expand, repository)


def expand_package(repository: Iterable[Package], package: Package) -> Package:
    expand = partial(expand_reference, repository)
    package.dependencies = list(map(lambda d: list(map(expand, d)),
                                    package.dependencies))
    package.conflicts = list(map(expand, package.conflicts))
    return package


def expand_reference(repository: Iterable[Package],
                     reference: PackageReference) -> PackageGroup:
    p_group = list(filter(lambda p: p.identifier.name == reference.identifier.name
                          and (reference.compare(p.identifier.version,
                                                 reference.identifier.version)
                          if reference.compare else True), repository))
    return PackageGroup(reference.identifier, p_group)
