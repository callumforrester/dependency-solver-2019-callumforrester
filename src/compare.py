from typing import TypeVar, Callable

from src.package import Package, Repository, Relations


GREATER = '>'
GREATER_OR_EQUAL = '>='
EQUAL = '='
LESS_OR_EQUAL = '<='
LESS = '<'

# Deps format: [[A OR B] AND [C]]


# TODO: Make this less tight-looped
def flatten_repository(repository: Repository) -> Repository:
    for package, relations in repository.items():
        dependencies = []
        conflicts = []
        for dependency_disjunct in relations.dependencies:
            new_disjunct = []
            for dependency in dependency_disjunct:
                new_disjunct += flatten_reference(repository, dependency)
            dependencies.append(new_disjunct)
        for conflict in relations.conflicts:
            conflicts += flatten_reference(repository, conflict)
        repository[package] = Relations(
            relations.size,
            dependencies,
            conflicts
        )
    return repository


def flatten_reference(repo: Repository, reference: str):
    check = filter_for_operator(reference)
    return list(filter(check, repo.keys()))


def filter_for_operator(reference: str) -> Callable[[Package], bool]:
    if GREATER_OR_EQUAL in reference:
        return filter_for(reference, GREATER_OR_EQUAL)
    elif GREATER in reference:
        return filter_for(reference, GREATER)
    elif LESS_OR_EQUAL in reference:
        return filter_for(reference, LESS_OR_EQUAL)
    elif LESS in reference:
        return filter_for(reference, LESS)
    elif EQUAL in reference:
        return filter_for(reference, EQUAL)
    else:
        return lambda p: p.name == reference


def filter_for(reference: str, operator: str) -> Callable[[Package], bool]:
    args = reference.split(operator)
    name = args[0]
    version = args[1]

    cmp = compare(operator)
    return lambda p: p.name == name and cmp(p.version, version)


TComparable = TypeVar('TComparable')


def compare(operator: str) -> Callable[[TComparable, TComparable], bool]:
    return {
        GREATER: lambda a, b: a > b,
        GREATER_OR_EQUAL: lambda a, b: a >= b,
        EQUAL: lambda a, b: a == b,
        LESS_OR_EQUAL: lambda a, b: a <= b,
        LESS: lambda a, b: a < b
    }[operator]
