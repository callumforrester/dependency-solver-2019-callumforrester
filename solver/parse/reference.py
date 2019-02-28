import re

from typing import List, Iterable, Dict, Optional

from solver.package.package import PackageReference, Version
from solver.compare import VersionOperator

PACKAGE_REFERENCE_REGEX = '([.+a-zA-Z0-9-]+)(?:(>=|<=|=|<|>)(\d+(?:\.\d+)*))?'


def parse_package_identifier(d: Dict) -> PackageReference:
    return make_package_reference(d['name'], d['version'])


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


def make_package_reference(name: str, version: str,
                           operator: str = None) -> PackageReference:
    return PackageReference(name, parse_version(version),
                            VersionOperator(operator)
                            if operator else VersionOperator.EQUAL)

def parse_version(version: Optional[str]) -> Optional[Version]:
    if version is None:
        return version
    else:
        return tuple(map(int, version.split('.')))
