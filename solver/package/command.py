from dataclasses import dataclass
from enum import Enum

from solver.package.package import PackageReference


class CommandSort(Enum):
    INSTALL = '+'
    UNINSTALL = '-'


@dataclass
class Command:
    sort: CommandSort
    reference: PackageReference

    def __str__(self) -> str:
        return '%s%s' % (self.sort.value, self.reference)
