import json
import re

from typing import List, Dict, Iterator, Iterable, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

from src.compare import compare


Version = str


PACKAGE_REFERENCE_REGEX = '([.+a-zA-Z0-9-]+)(?:(>=|<=|=|<|>)(\d+(?:\.\d+)*))?'
COMMAND_REGEX = '([+-])%s' % PACKAGE_REFERENCE_REGEX


old_map = map
map = lambda fn, it: list(old_map(fn, it))


# PackageGroup = Iterable['Package']
Constraint = Union['PackageGroup', 'PackageReference']


@dataclass(eq=True, frozen=True)
class PackageIdentifier:
    name: str
    version: Version

    def unique_name(self) -> str:
        return '%s_%s' % (self.name, self.version)

    def __str__(self) -> str:
        return '%s=%s' % (self.name, self.version)


@dataclass
class PackageReference:
    identifier: PackageIdentifier
    compare: Callable[[Version, Version], bool]


@dataclass
class PackageGroup:
    identifier: PackageIdentifier
    packages: Iterable['Package']


class CommandSort(Enum):
    INSTALL = '+'
    UNINSTALL = '-'


@dataclass
class Command:
    sort: CommandSort
    reference: Constraint

    def __str__(self) -> str:
        return '%s%s' % (self.sort.value, self.reference)


@dataclass
class Package:
    identifier: PackageIdentifier
    size: int
    dependencies: List[List[Constraint]]
    conflicts: List[Constraint]


def parse_repository(repository: List[Dict]) -> Iterable[Package]:
    return map(parse_package, repository)


def parse_package(d: Dict) -> Package:
    return Package(
        PackageIdentifier(d['name'], parse_version(d['version'])),
        d['size'],
        parse_dependencies(d['depends']) if 'depends' in d else [],
        parse_package_references(d['conflicts']) if 'conflicts' in d else []
    )

def parse_version(version: str) -> Version:
    return version


def parse_dependencies(dependencies: List[List[str]]) -> Iterable[Iterable[
                                                         PackageReference]]:
    return map(parse_package_references, dependencies)


def parse_package_references(references: List[str]) -> Iterable[
                                                        PackageReference]:
    return map(parse_package_reference, references)


def parse_package_reference(reference: str) -> PackageReference:
        name, operator, version = re\
                                    .compile(PACKAGE_REFERENCE_REGEX)\
                                    .match(reference)\
                                    .groups()
        return make_package_reference(name, version, operator)


def parse_command_list(commands: List[str]) -> Iterable[Command]:
    return map(parse_command, commands)


def parse_command(command: str) -> Command:
    plus_minus, name, operator, version = re.compile(COMMAND_REGEX)\
                                            .match(command)\
                                            .groups()
    return Command(CommandSort(plus_minus), make_package_reference(name, version, operator))


def make_package_reference(name, version, operator) -> PackageReference:
            parsed_version = parse_version(version) if version else None
            return PackageReference(PackageIdentifier(name, parsed_version),
                                    compare(operator) if operator else None)


def load_dict(file_path: str) -> Iterator[Dict]:
    with open(file_path, 'r') as handle:
        return json.load(handle)
