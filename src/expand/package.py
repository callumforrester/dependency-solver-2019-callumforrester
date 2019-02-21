from functools import partial

from src.package.package import Package, PackageReference, PackageGroup, Repository


def expand_repository(repository: Repository) -> PackageGroup:
    result = {}
    for name, packages in repository.items():
        for reference, package in packages.items():
            result[reference] = expand_package(repository, package)
    return result


def expand_package(repository: Repository, package: Package) -> Package:
    expand = partial(expand_reference, repository)
    return Package(package.size,
                   list(map(lambda d: list(map(expand, d)),
                            package.dependencies)),
                   list(map(expand, package.conflicts)))


def expand_reference(repository: Repository,
                     reference: PackageReference) -> PackageGroup:
    name = reference.name
    if name in repository:
        candidates = repository[reference.name]
        return list(filter(reference.compare, candidates))
    else:
        return []
