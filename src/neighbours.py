import itertools

from typing import TypeVar, Iterable, Tuple

TNeighbour = TypeVar('TNeighbour')


def neighbours(it: Iterable[TNeighbour]) -> Iterable[
                                            Tuple[TNeighbour, TNeighbour]]:
    return zip(it, itertools.islice(it, 1, None))
