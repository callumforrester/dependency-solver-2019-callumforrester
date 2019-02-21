from z3 import ModelRef
from typing import Iterable, Any, List

from src.package.package import PackageGroup
from src.package.command import Command, CommandSort
from src.neighbours import neighbours
from src.encode.state import EncodedState


def decode(model: ModelRef, state: List[EncodedState],
           repository: PackageGroup) -> Iterable[Command]:
    all_commands = (to_command(model, from_state, to_state)
                    for from_state, to_state in neighbours(state))

    return list(filter(is_not_none, all_commands))


def to_command(model: ModelRef, before: EncodedState,
               after: EncodedState) -> Command:
    for p in before.keys():
        installed_before = bool(model.eval(before[p]))
        installed_after = bool(model.eval(after[p]))

        if (not installed_before) and installed_after:
            return Command(CommandSort.INSTALL, p)
        elif installed_before and (not installed_after):
            return Command(CommandSort.UNINSTALL, p)
    return None


def is_not_none(a: Any) -> bool:
    return a is not None
