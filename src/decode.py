import itertools

from z3 import ModelRef, Z3PPObject, BoolRef
from typing import Iterable, Dict, Any

from src.package import Command, CommandSort, Package, PackageIdentifier
from src.encode import BoolRepository, neighbours


def decode(model: ModelRef, bools: BoolRepository,
           repository: Iterable[Package], time_steps: Iterable[int]) -> Iterable[Command]:
    sequence = filter(is_not_none,
                      (to_command(model, bools[t0], bools[t1])
                       for t0, t1 in neighbours(time_steps)))
    return list(sequence)


def to_command(model: ModelRef, before: Dict[PackageIdentifier, BoolRef],
               after: Dict[PackageIdentifier, BoolRef]) -> Command:
    # packages = set(before) - set(after)
    # print('%s -> %s' % (before, after))

    for p in before.keys():
        installed_before = bool(model.eval(before[p]))
        installed_after = bool(model.eval(after[p]))
        # print('%s -> %s' % (installed_before, installed_after))
        if (not installed_before) and installed_after:
            return Command(CommandSort.INSTALL, p)
        elif installed_before and (not installed_after):
            return Command(CommandSort.UNINSTALL, p)
    return None


def is_not_none(a: Any) -> bool:
    return a is not None