import logging
from tqdm import tqdm
from typing import Iterable


def logging_tqdm(it: Iterable, min_level: int = logging.INFO) -> tqdm:
    should_disable = logging.getLogger().level > min_level
    return tqdm(it, disable=should_disable)
