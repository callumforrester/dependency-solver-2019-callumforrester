import json
import re

from typing import List, Dict, Iterator, Iterable, Callable, Union
from dataclasses import dataclass
from enum import Enum
from tqdm import tqdm

from src.compare import VersionOperator, compare


PACKAGE_REFERENCE_REGEX = '([.+a-zA-Z0-9-]+)(?:(>=|<=|=|<|>)(\d+(?:\.\d+)*))?'
COMMAND_REGEX = '([+-])%s' % PACKAGE_REFERENCE_REGEX

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


class CommandSort(Enum):
    INSTALL = '+'
    UNINSTALL = '-'


@dataclass
class Command:
    sort: CommandSort
    reference: PackageReference

    def __str__(self) -> str:
        return '%s%s' % (self.sort.value, self.reference)


@dataclass
class Package:
    size: int
    dependencies: List[List[PackageReference]]
    conflicts: List[PackageReference]


def parse_repository(repository: List[Dict]) -> PackageGroup:
    rep = {}
    for d in tqdm(repository):
        identifier = parse_package_identifier(d)
        package = parse_package(d)
        name = identifier.name
        if name not in rep:
            rep[name] = {}
        rep[name][identifier] = package
    return rep


def parse_package_identifier(d: Dict) -> PackageReference:
    return PackageReference(
        d['name'],
        d['version']
    )


def parse_package(d: Dict) -> Package:
    return Package(
        d['size'],
        list(parse_dependencies(d['depends']) if 'depends' in d else []),
        list(parse_package_references(d['conflicts']) if 'conflicts' in d else [])
    )


def parse_dependencies(dependencies: List[List[str]]) -> Iterable[Iterable[
                                                         PackageReference]]:
    return map(parse_package_references, dependencies)


def parse_package_references(references: List[str]) -> Iterable[
                                                        PackageReference]:
    return map(parse_package_reference, references)


def parse_package_reference(reference: str) -> PackageReference:
    name, operator, version = re.compile(PACKAGE_REFERENCE_REGEX)\
                                .match(reference)\
                                .groups()
    return make_package_reference(name, version, operator)


def parse_command_list(commands: List[str]) -> Iterable[Command]:
    return map(parse_command, commands)


def parse_command(command: str) -> Command:
    plus_minus, name, operator, version = re.compile(COMMAND_REGEX)\
                                            .match(command)\
                                            .groups()
    return Command(CommandSort(plus_minus),
                   make_package_reference(name, version, operator))


def make_package_reference(name, version, operator) -> PackageReference:
    return PackageReference(name, version,
                            VersionOperator(operator)
                            if operator else VersionOperator.EQUAL)


def load_json(file_path: str) -> Iterator[Dict]:
    with open(file_path, 'r') as handle:
        return json.load(handle)
