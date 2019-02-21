import json
import re

from typing import List, Dict
from dataclasses import dataclass

from src.compare import VersionOperator, compare


# Constraint = Union['PackageGroup', 'PackageReference']
PackageGroup = Dict['PackageReference', 'Package']
Repository = Dict[str, PackageGroup]
# Hmmm


@dataclass(eq=True, frozen=True)
class PackageReference:
    name: str
    version: str
    operator: VersionOperator = VersionOperator.EQUAL

    def __str__(self) -> str:
        return '%s%s%s' % (self.name, self.operator.value, self.version)

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
