import logging

from z3 import BoolRef, And, Not
from typing import Iterable
from tqdm import tqdm

from src.encode.bools import BoolGroup
from src.encode.install import get_bools
from src.package.command import Command, CommandSort
from src.debug import in_debug


def constrain_commands(bools: BoolGroup,
                       commands: Iterable[Command]) -> BoolRef:
    logging.debug('final state constraint')
    return And([command_to_bool(bools, c) for c in tqdm(commands, disable=in_debug())])


def command_to_bool(bools: BoolGroup, command: Command) -> BoolRef:
    req = get_bools(bools, command.reference)[0]
    return {
        CommandSort.INSTALL: req,
        CommandSort.UNINSTALL: Not(req)
    }[command.sort]
