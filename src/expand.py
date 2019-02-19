from tqdm import tqdm
from typing import Iterable
from functools import partial, reduce

from src.package import Package, Command, PackageReference, PackageGroup, Repository


def expand_commands(repository: Repository,
                    commands: Iterable[Command]) -> Iterable[Command]:
    expand = partial(expand_command, repository)
    return map(expand, commands)


def expand_command(repository: Repository, command: Command) -> Command:
    command.reference = expand_reference(repository, command.reference)
    return command


def expand_repository(repository: Repository) -> PackageGroup:
    result = {}
    for name, packages in tqdm(repository.items()):
        for reference, package in packages.items():
            result[reference] = expand_package(repository, package)
    return result


def expand_package(repository: Repository, package: Package) -> Package:
    expand = partial(expand_reference, repository)
    return Package(package.size,
                   list(map(lambda d: list(map(expand, d)), package.dependencies)),
                   list(map(expand, package.conflicts)))


def expand_reference(repository: Repository,
                     reference: PackageReference) -> PackageGroup:
    name = reference.name
    if name in repository:
        candidates = repository[reference.name]
        return list(filter(reference.compare, candidates))
    else:
        return []
