from army.api.log import log
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
from army.army import prefix
from army.api.click import verbose_option 
from army.api.package import load_installed_packages, load_installed_package
from army.army import cli
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

@cli.command(name='install', help='Install package')
@verbose_option()
@click.option('-l', '--link', help='Link files instead of copy (local repository only)', is_flag=True)
@click.option('-g', '--global', help='Install module in user space', is_flag=True)
@click.option('-r', '--reinstall', help='Force reinstall module if already exists', is_flag=True)
# @click.option('--save', help='Update project package list', is_flag=True)    # TODO
@click.argument('name', nargs=-1)
@click.pass_context
def install(ctx, name, link, reinstall, **kwargs):
    log.info(f"install {name} {kwargs}")
    
    _global = kwargs['global']  # not in parameters due to conflict with global keywoard
    
    # load configuration
    config = ctx.parent.config
    project = None
    try:
        # load project configuration
        project = load_project()
    except Exception as e:
        print_stack()
        log.debug(e)
        log.info(f"no project loaded")
    
    if len(name)==0 and project is None:
        print("nothing to install", file=sys.stderr)
        exit(1)
        
    # build repositories list
    repositories = load_repositories(config, prefix)
    
    packages = []

    if len(name)==0:
        if project is None:
            log.error(f"{os.getcwd()}: army.toml not found")
            exit(1)

        for package in project.dependencies:
            pkg, repo = _find_package(package, project.dependencies[package], repositories)
            packages.append(PackageDependency(package=pkg, repository=repo))
            
        for plugin in project.plugins:
            pkg, repo = _find_package(plugin, project.plugins[plugin], repositories)
            packages.append(PackageDependency(package=pkg, repository=repo))
    else:
        for package in name:
            pkg, repo = _find_package(package, repositories)
            packages.append(PackageDependency(package=pkg, repository=repo))

    # locate install folder
    if _global:
        path = os.path.join(prefix, "~/.army/dist/")
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
            pkg, repo = _find_package(dependency, package.dependencies[dependency], repositories)
            dep_pkg = PackageDependency(package=pkg, repository=repo, from_package=package)
            packages.append(dep_pkg)

        # append plugins to list
        for plugin in package.plugins:
            pkg, repo = _find_package(plugin, package.plugins[plugin], repositories)
            dep_pkg = PackageDependency(package=pkg, repository=repo, from_package=package)
            packages.append(dep_pkg)

    # treat dependencies first
    dependencies.reverse()
    
    log.debug(f"packages: {dependencies}")
    # checks
    _check_dependency_version_conflict(dependencies)
    _check_installed_version_conflict(dependencies)
    
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
            if dependency.repository.DEV==True:
                dependency.package.install(path=os.path.join(path, dependency.package.name), link=link)
            else:
                # link mode is only possible with repository DEV
                dependency.package.install(path=os.path.join(path, dependency.package.name), link=False)
    
    # TODO save and save-dev

def _check_dependency_version_conflict(dependencies):
    """ Check if dependencies contains same package with version mismatch
    """
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
    
def _find_package(name, version, repositories):
    # search for module in repositories
    for repo in repositories:
        res = repo.search(name, version, fullname=True)
        if len(res)>0:
            # result can contain only one element as fullname is True
            for package in res:
                return res[package], repo
    print(f"{package}: package not found", file=sys.stderr)
    exit(1)
    