from army.api.log import log
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
from army import prefix
from army.api.click import verbose_option 
from army.api.package import load_installed_packages, load_installed_package
from army import cli, dependencies
import click
import os
import sys

class PackageDependency(object):
    def __init__(self, package, repository, from_package=None):
        self._package = package
        self._from_package = from_package
        self._repository = repository
        
    @property 
    def package(self):
        return self._package
    
    @property
    def from_package(self):
        return self._from_package

    @property
    def repository(self):
        return self._repository

    def __repr__(self):
        return f"{self._package.name}:{self._package.version}"

@dependencies.command(name='install', help='Install package')
@verbose_option()
@click.option('-l', '--link', help='Link files instead of copy (local repository only)', is_flag=True)
# @click.option('-g', '--global', help='Install module in user space', is_flag=True)
@click.option('-r', '--reinstall', help='Force reinstall module if already exists', is_flag=True)
# @click.option('--save', help='Update project package list', is_flag=True)    # TODO
@click.argument('name', nargs=-1)
@click.pass_context
def install(ctx, name, link, reinstall, **kwargs):
    log.info(f"install {name} {kwargs}")
    
    _global = kwargs['global']  # not in parameters due to conflict with global keywoard
    
    # load configuration
    config = ctx.parent.config
    
    # load project
    project = ctx.parent.project
    if project is None:
        log.info(f"no project loaded")

    # get target config
    target = ctx.parent.target
    if target is None:
        print(f"no target specified", file=sys.stderr)
        exit(1)

    if len(name)==0 and project is None:
        print("nothing to install", file=sys.stderr)
        exit(1)
        
    # build repositories list
    repositories = load_repositories(config, prefix)
    
    for repository in repositories:
        if repository.load_credentials()==False:
            print(f"{repository.name}: warning: load credentials failed, update may fail due to rate limitation", file=sys.stderr)
        
    packages = []

    if len(name)==0:
        if project is None:
            log.error(f"{os.getcwd()}: army.toml not found")
            exit(1)

        for package in project.dependencies:
            pkg, repo = _find_package(package, project.dependencies[package], repositories, priority_dev=link)
            packages.append(PackageDependency(package=pkg, repository=repo))

        if target is not None:
            for package in target.dependencies:
                pkg, repo = _find_package(package, target.dependencies[package], repositories, priority_dev=link)
                packages.append(PackageDependency(package=pkg, repository=repo))
            
        for plugin in project.plugins:
            pkg, repo = _find_package(plugin, project.plugins[plugin], repositories, plugin=True, priority_dev=link)
            packages.append(PackageDependency(package=pkg, repository=repo))
        
        if target is not None:
            for plugin in target.plugins:
                pkg, repo = _find_package(plugin, target.plugins[plugin], repositories, plugin=True, priority_dev=link)
                packages.append(PackageDependency(package=pkg, repository=repo))
    else:
        for package in name:
            if ':' in package:
                package, version = package.split(':')
            else:
                version = 'latest'
            pkg, repo = _find_package(package, version, repositories, priority_dev=link)
            packages.append(PackageDependency(package=pkg, repository=repo))

    # locate install folder
    if _global:
        path = os.path.join(prefix or "", "~/.army/dist/")
    else:
        path = "dist"
    
    force = False
    if reinstall:
        force = True

    dependencies = []
    while(len(packages)>0):
        # get dependencies from top level package to end level
        package_dep = packages.pop(0)
        package = package_dep.package

        # dependency treated ok, append to list
        dependencies.append(package_dep)
        
        # append dependencies to list
        for dependency in package.dependencies:
            pkg, repo = _find_package(dependency, package.dependencies[dependency], repositories, priority_dev=link)
            dep_pkg = PackageDependency(package=pkg, repository=repo, from_package=package)
            packages.append(dep_pkg)

        # append plugins to list
        for plugin in package.plugins:
            pkg, repo = _find_package(plugin, package.plugins[plugin], repositories, priority_dev=link)
            dep_pkg = PackageDependency(package=pkg, repository=repo, from_package=package)
            packages.append(dep_pkg)

    # treat dependencies first
    dependencies.reverse()

    log.debug(f"packages: {dependencies}")
    
    # TODO checks
    _check_dependency_version_conflict(dependencies)
    _check_installed_version_conflict(dependencies)
    
    # TODO clean dependency duplicates to avoid installing several times same package
    dependencies = _remove_duplicates(dependencies)
    
    # install
    for dependency in dependencies:
        install = False
        installed_package = load_installed_package(dependency.package.name, prefix=prefix)
        if installed_package:
            if force==True:
                print(f"reinstall {dependency.package}")
                install = True
            else:
                print(f"package {dependency.package} already installed")
                install = False
        else:
            install = True
            print(f"install package {dependency.package}")
            
        if install==True:
            if link==True and dependency.repository.DEV==False:
                print(f"{dependency.package.name}: repository is not local, link not applied", file=sys.stderr)
            if dependency.repository.DEV==True:
                dependency.package.install(path=os.path.join(path, dependency.package.name), link=link)
            else:
                # link mode is only possible with repository DEV
                dependency.package.install(path=os.path.join(path, dependency.package.name), link=False)
    
    # TODO save and save-dev

def _check_dependency_version_conflict(dependencies):
    """ Check if dependencies contains same package with version mismatch
    """
    # TODO: use VersionRange to true comparaison
    
    for dependency in dependencies:
        for dep in dependencies:
            if dep.package.name==dependency.package.name and dep.package.version!=dependency.package.version:
                msg = f"'{dependency.package.name}': version conflicts: "
                if dependency.from_package is None:
                    msg += f"'{dependency.package.version}' from project"
                else:
                    msg += f"'{dependency.package.version}' from '{dependency.from_package.name}'"
                msg += " conflicts with "
                if dep.from_package is None:
                    msg += f"'{dep.package.version}' from project"
                else:
                    msg += f"'{dep.package.version}' from '{dep.from_package.name}'"
                print(msg, file=sys.stderr)
                exit(1)

def _check_installed_version_conflict(dependencies):
    """ Check if dependencies contains a package already installed with a version mismatch
    """
    installed = load_installed_packages(prefix=prefix)
    # TODO
    
def _find_package(name, version_range, repositories, plugin=False, priority_dev=False):
    """ search for a package in repositories
    package with the greatest version in version_range is returned
    if priority_dev is True _find_package will try to match a local dev repository if possible 
    
    :param name: name of the package to find
    :param version_range: version range to match, if None then match 'latest'
    :param repositories: list of repositories to search into
    :param plugin: indicates if search package is a plugin, plugin names terminate by '-plugin'
    :param priority_dev: if True _find_package will try to find a suitable version with a local dev repository
    """

    if plugin and name.endswith("-plugin")==False:
        name = f"{name}-plugin"

    # result can contain only one element as fullname is True
    res_package = None
    res_repo = None
    for repo in repositories:
        # search a package in repo that matches name and version
        packages_found = repo.search(name, version_range, fullname=True)

        for package_found in packages_found:
            package = packages_found[package_found]
#             if package.version in 
            if res_package is None:
                res_package = package
                res_repo = repo
            elif package.version>res_package.version:
                res_package = package
                res_repo = repo
            elif priority_dev==True and repo.DEV==True and res_package.repository.DEV==False and package.version>=res_package.version:
                # previous match was not a dev repository and current match is version ok
                res_package = package
                res_repo = repo

    if res_package:
        return res_package, res_repo

    print(f"{name}: package not found", file=sys.stderr)
    exit(1)

def _remove_duplicates(dependencies):
    """ remove install duplicates inside dependencies
    """
    res = []
    
    for dependency in dependencies:
        found = False
        for search_dep in res:
            if dependency.package==search_dep.package:
                found = True
                break
        
        if found==False:
            res.append(dependency)
        
    return res
