import json

from typing import List, Dict, Iterator
from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class Package:
    name: str
    version: str
    size: int


@dataclass
class Constraints:
    dependencies: List[List[Package]]
    conflicts: List[Package]


Repository = Dict[Package, Constraints]


def parse_repository(repository: List[Dict]) -> Repository:
    return {
        parse_package(d): parse_package_constraints(d)
        for d in repository
    }


def parse_package(d: Dict) -> Package:
    return Package(
        d['name'],
        d['version'],
        d['size']
    )


def parse_package_constraints(d: Dict) -> Constraints:
    return Constraints(
        d['depends'] if 'depends' in d else [],
        d['conflicts'] if 'conflicts' in d else []
    )


def load_dict(file_path: str) -> Iterator[Dict]:
    with open(file_path, 'r') as handle:
        return json.load(handle)
