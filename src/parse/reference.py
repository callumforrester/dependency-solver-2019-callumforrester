import re

from typing import List, Iterable, Dict

from src.package.package import PackageReference
from src.compare import VersionOperator

PACKAGE_REFERENCE_REGEX = '([.+a-zA-Z0-9-]+)(?:(>=|<=|=|<|>)(\d+(?:\.\d+)*))?'


def parse_package_identifier(d: Dict) -> PackageReference:
    return PackageReference(
        d['name'],
        d['version']
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


def make_package_reference(name, version, operator) -> PackageReference:
    return PackageReference(name, version,
                            VersionOperator(operator)
                            if operator else VersionOperator.EQUAL)
