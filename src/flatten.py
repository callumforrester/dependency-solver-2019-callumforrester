import itertools

from typing import Iterable, List, TypeVar


TIterated = TypeVar('TIterable')


def flatten(it: Iterable[Iterable[TIterated]]) -> Iterable[TIterated]:
    return itertools.chain.from_iterable(it)


def flatten_as_list(it: Iterable[Iterable[TIterated]]) -> List[TIterated]:
    return list(flatten(it))
