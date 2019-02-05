import json

from typing import List, Dict, Iterator
from dataclasses import dataclass


@dataclass
class Package:
    name: str
    version: str
    size: int
    dependencies: List[List[str]]
    conflicts: List[str]


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
