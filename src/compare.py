from typing import TypeVar, Callable


GREATER = '>'
GREATER_OR_EQUAL = '>='
EQUAL = '='
LESS_OR_EQUAL = '<='
LESS = '<'

# Deps format: [[A OR B] AND [C]]


TComparable = TypeVar('TComparable')


def compare(operator: str) -> Callable[[TComparable, TComparable], bool]:
    return {
        GREATER: lambda a, b: a > b,
        GREATER_OR_EQUAL: lambda a, b: a >= b,
        EQUAL: lambda a, b: a == b,
        LESS_OR_EQUAL: lambda a, b: a <= b,
        LESS: lambda a, b: a < b
    }[operator]
