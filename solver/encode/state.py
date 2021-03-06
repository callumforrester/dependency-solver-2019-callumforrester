import logging

from z3 import BoolRef, Bool
from typing import List, Iterable, Dict

from solver.package.package import PackageReference, PackageGroup
from solver.debug import logging_tqdm

EncodedState = Dict[PackageReference, BoolRef]


def generate_state_map(repository: PackageGroup,
                       time_range: Iterable[int]) -> List[EncodedState]:
    logging.info('generating state map')
    return [{reference: to_bool(reference, time_step)
             for reference in repository}
            for time_step in logging_tqdm(time_range)]


def to_bool(reference: PackageReference, time_step: int) -> Bool:
    return Bool('%s_%i' % (reference, time_step))
