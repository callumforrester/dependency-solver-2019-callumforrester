import json

from typing import List, Dict, Iterator, Tuple
from dataclasses import dataclass


@dataclass
class Package:
    name: str
    version: str
    size: int
    dependencies: List[List[str]]
    conflicts: List[str]


Repository = Dict[Tuple[str, str], Package]


def parse_repository(repository: List[Dict]) -> Repository:
    return {
        (d['name'], d['version']): parse(d)
        for d in repository
    }


def parse(d: Dict) -> Package:
    return Package(
        d['name'],
        d['version'],
        d['size'],
        d['dependencies'] if 'dependencies' in d else [],
        d['conflicts'] if 'conflicts' in d else []
    )


def load_dict(file_path: str) -> Iterator[Dict]:
    with open(file_path, 'r') as handle:
        return json.load(handle)
