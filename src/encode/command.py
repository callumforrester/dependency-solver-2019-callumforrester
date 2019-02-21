import logging

from z3 import BoolRef, And, Not
from typing import Iterable
from tqdm import tqdm

from src.encode.bools import BoolGroup
from src.encode.install import find_bools
from src.package.package import Command, CommandSort
from src.debug import in_debug


def constrain_commands(bools: BoolGroup,
                       commands: Iterable[Command]) -> BoolRef:
    logging.debug('final state constraint')
    return And([command_to_bool(bools, c) for c in tqdm(commands, disable=in_debug())])


def command_to_bool(bools: BoolGroup, command: Command) -> BoolRef:
    req = next(find_bools(bools, command.reference))
    return {
        CommandSort.INSTALL: req,
        CommandSort.UNINSTALL: Not(req)
    }[command.sort]
