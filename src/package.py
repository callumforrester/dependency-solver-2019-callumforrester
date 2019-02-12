import json
import re

from typing import List, Dict, Iterator, Iterable, Callable
from dataclasses import dataclass
from functools import partial

from src.compare import compare


Version = str


PACKAGE_REFERENCE_REGEX = '([.+a-zA-Z0-9-]+)(?:(>=|<=|=|<|>)(\d+(?:\.\d+)*))?'
COMMAND_REGEX = '([+-])%s' % PACKAGE_REFERENCE_REGEX


old_map = map
map = lambda fn, it: list(old_map(fn, it))


@dataclass
class PackageReference:
    name: str
    version: Version
    compare: Callable[[Version, Version], bool]


@dataclass
class Command:
    plus_minus: str
    reference: PackageReference


@dataclass
class Package:
    name: str
    version: Version
    size: int
    dependencies: List[List[PackageReference]]
    conflicts: List[PackageReference]


def parse_repository(repository: List[Dict]) -> Iterable[Package]:
    return map(parse_package, repository)


def parse_package(d: Dict) -> Package:
    return Package(
        d['name'],
        parse_version(d['version']),
        d['size'],
        parse_dependencies(d['depends']) if 'depends' in d else [],
        parse_package_references(d['conflicts']) if 'conflicts' in d else []
    )


def parse_version(version: str) -> Version:
    # return list(map(int, version.split('.')))
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
    return Command(plus_minus, make_package_reference(name, version, operator))


def make_package_reference(name, version, operator) -> PackageReference:
            parsed_version = parse_version(version) if version else None
            return PackageReference(name, parsed_version,
                                    compare(operator) if operator else None)


def load_dict(file_path: str) -> Iterator[Dict]:
    with open(file_path, 'r') as handle:
        return json.load(handle)
