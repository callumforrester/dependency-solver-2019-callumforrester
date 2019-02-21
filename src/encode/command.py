import logging

from z3 import BoolRef, And, Not
from typing import Iterable
from tqdm import tqdm

from src.encode.state import EncodedState
from src.encode.install import get_state
from src.package.command import Command, CommandSort
from src.debug import in_debug


def constrain_commands(state: EncodedState,
                       commands: Iterable[Command]) -> BoolRef:
    logging.debug('final state constraint')
    return And([command_to_bool(state, c) for c in tqdm(commands, disable=in_debug())])


def command_to_bool(state: EncodedState, command: Command) -> BoolRef:
    req = get_state(state, command.reference)[0]
    return {
        CommandSort.INSTALL: req,
        CommandSort.UNINSTALL: Not(req)
    }[command.sort]
