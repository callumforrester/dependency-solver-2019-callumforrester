from typing import Iterable
from functools import partial, reduce

from src.package import Package, Command, PackageReference, PackageGroup, Repository


def expand_commands(repository: Iterable[Package],
                    commands: Iterable[Command]) -> Iterable[Command]:
    expand = partial(expand_command, repository)
    return map(expand, commands)


def expand_command(repository: Iterable[Package], command: Command) -> Command:
    command.reference = expand_reference(repository, command.reference)
    return command


def expand_repository(repository: Repository) -> Repository:
    return {
        name: expand_package_group(repository, packages)
        for name, packages in repository.items()
    }


def expand_package_group(repository: Repository, group: PackageGroup) -> PackageGroup:
    return {
        identifier: expand_package(repository, package)
        for identifier, package in group.items()
    }


def expand_package(repository: Repository, package: Package) -> Package:
    expand = partial(expand_reference, repository)
    return Package(package.size,
                   list(map(lambda d: list(map(expand, d)), package.dependencies)),
                   list(map(expand, package.conflicts)))


def expand_reference(repository: Repository,
                     reference: PackageReference) -> PackageGroup:
    candidates = repository[reference.name]
    return list(filter(reference.compare, candidates))
