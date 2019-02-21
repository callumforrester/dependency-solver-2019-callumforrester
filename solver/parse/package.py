from typing import List, Dict

from solver.package.package import Package, PackageGroup
from solver.parse.reference import parse_package_identifier, parse_dependencies, \
                                parse_package_references


def parse_repository(repository: List[Dict]) -> PackageGroup:
    rep = {}
    for d in repository:
        identifier = parse_package_identifier(d)
        package = parse_package(d)
        name = identifier.name
        if name not in rep:
            rep[name] = {}
        rep[name][identifier] = package
    return rep


def parse_package(d: Dict) -> Package:
    return Package(
        d['size'],
        list(parse_dependencies(d['depends']) if 'depends' in d else []),
        list(parse_package_references(d['conflicts']) if 'conflicts' in d else [])
    )
