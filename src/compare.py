from typing import TypeVar, Callable, Iterator, Iterable
from functools import partial

from src.package import Package


GREATER = '>'
GREATER_OR_EQUAL = '>='
EQUAL = '='
LESS_OR_EQUAL = '<='
LESS = '<'


def parse_reference(reference: str) -> Callable[[Iterable[Package]], Iterator[Package]]:
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
        return partial(filter, lambda p: p.name == reference)


def filter_for(reference: str,
               operator: str) -> Callable[[Iterable[Package]], Iterator[Package]]:
    args = reference.split(operator)
    name = args[0]
    version = args[1]

    return partial(filter, lambda p: p.name == name and p.version == version)


TComparable = TypeVar('TComparable')


def compare(operator: str) -> Callable[[TComparable, TComparable], bool]:
    return {
        GREATER: lambda a, b: a > b,
        GREATER_OR_EQUAL: lambda a, b: a >= b,
        EQUAL: lambda a, b: a == b,
        LESS_OR_EQUAL: lambda a, b: a <= b,
        LESS: lambda a, b: a < b
    }[operator]
