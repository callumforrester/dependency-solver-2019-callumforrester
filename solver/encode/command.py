import logging

from z3 import BoolRef, And, Not
from typing import Iterable

from solver.encode.state import EncodedState
from solver.encode.install import get_state
from solver.package.command import Command, CommandSort
from solver.debug import logging_tqdm


def all_commands_obeyed(state: EncodedState,
                        commands: Iterable[Command]) -> BoolRef:
    logging.debug('final state constraint')
    return And([commands_obeyed(state, c)
                for c in logging_tqdm(commands)])


def commands_obeyed(state: EncodedState, command: Command) -> BoolRef:
    req = get_state(state, command.reference)[0]
    return {
        CommandSort.INSTALL: req,
        CommandSort.UNINSTALL: Not(req)
    }[command.sort]
