import logging


def in_debug() -> bool:
    return logging.getLogger().level >= logging.DEBUG
