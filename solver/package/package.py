import json
import re

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from solver.compare import VersionOperator, compare

PackageGroup = Dict['PackageReference', 'Package']
Repository = Dict[str, PackageGroup]
Version = Tuple[int, ...]


@dataclass(eq=True, frozen=True)
class PackageReference:
    name: str
    version: Optional[Version]
    operator: VersionOperator = VersionOperator.EQUAL

    def __str__(self) -> str:
        version = version_to_str(self.version)
        return '%s%s%s' % (self.name, self.operator.value, version)

    def compare(self, other: 'PackageReference') -> bool:
        if self.version is None:
            return True
        else:
            return compare(self.operator)(other.version, self.version)


@dataclass
class Package:
    size: int
    dependencies: List[List[PackageReference]]
    conflicts: List[PackageReference]


def version_to_str(version: Version) -> str:
    return '.'.join(map(str, version))
