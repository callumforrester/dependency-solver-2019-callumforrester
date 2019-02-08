import json

from typing import List, Dict, Iterator, Tuple
from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class Package:
    name: str
    version: str


@dataclass
class Relations:
    size: int
    dependencies: List[List[Package]]
    conflicts: List[Package]


Repository = Dict[Package, Relations]


def parse_repository(repository: List[Dict]) -> Repository:
    return {
        parse_package(d): parse_relations(d)
        for d in repository
    }


def parse_package(d: Dict) -> Package:
    return Package(
        d['name'],
        d['version']
    )


def parse_relations(d: Dict) -> Relations:
    return Relations(
        d['size'],
        d['depends'] if 'depends' in d else [],
        d['conflicts'] if 'conflicts' in d else []
    )


def load_dict(file_path: str) -> Iterator[Dict]:
    with open(file_path, 'r') as handle:
        return json.load(handle)
