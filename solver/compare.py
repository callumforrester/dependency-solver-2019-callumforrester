from typing import TypeVar, Callable
from enum import Enum


class VersionOperator(Enum):
    GREATER = '>'
    GREATER_OR_EQUAL = '>='
    EQUAL = '='
    LESS_OR_EQUAL = '<='
    LESS = '<'

# Deps format: [[A OR B] AND [C]]


TComparable = TypeVar('TComparable')


def compare(operator: str) -> Callable[[TComparable, TComparable], bool]:
    return {
        VersionOperator.GREATER: lambda a, b: a > b,
        VersionOperator.GREATER_OR_EQUAL: lambda a, b: a >= b,
        VersionOperator.EQUAL: lambda a, b: a == b,
        VersionOperator.LESS_OR_EQUAL: lambda a, b: a <= b,
        VersionOperator.LESS: lambda a, b: a < b
    }[operator]
