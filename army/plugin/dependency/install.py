from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.log import log
from army.api.package import load_installed_package, find_repository_package
from army.api.path import prefix_path
from army.api.project import load_project
from army.api.repository import load_repositories
from army.api.version import Version, VersionRange
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
        return f"{self._repository.name}@{self._package.name}@{self._package.version}"

@parser
@group(name="dependency")
@command(name='install', help='Install package')
@option(name='edit', shortcut='e', default=False, help='Install packages from local repositories in edit mode', flag=True)
@option(name='global', shortcut='g', default=False, help='Install package in user space', flag=True)
@option(name='reinstall', shortcut='r', default=False, help='Force reinstall module if already exists', flag=True)
#@option(name='save', help='Update project package list', flag=True)    # TODO
@argument(name='name', count='*')
def install(ctx, name, edit, reinstall, **kwargs):
    log.info(f"install {name}")
    
    _global = kwargs['global']  # not in parameters due to conflict with global keyword
    
    # load configuration
    config = ctx.config
    
    # load project
    project = ctx.project
    if project is None:
        log.info(f"no project loaded")

    if len(name)==0 and project is None:
        print("nothing to install", file=sys.stderr)
        exit(1)
        
    # build repositories list
    repositories = load_repositories(config)
     
    for repository in repositories:
        if repository.load_credentials()==False:
            print(f"{repository.name}: warning: load credentials failed, update may fail due to rate limitation", file=sys.stderr)
         
    packages = []
 
    if len(name)==0:
#         # get target config
#         target = ctx.target
#         if target is None:
#             print(f"no target specified", file=sys.stderr)
#             exit(1)

        for package, version in project.dependencies.items():
            pkg, repo = _find_repository_package(repositories, package, version_range=version, editable=edit)
            packages.append(PackageDependency(package=pkg, repository=repo))

#         if target is not None:
#             for package in target.dependencies:
#                 pkg, repo = _find_package(package, target.dependencies[package], repositories, priority_dev=link)
#                 packages.append(PackageDependency(package=pkg, repository=repo))
#             
#         for plugin in project.plugins:
#             pkg, repo = _find_package(plugin, project.plugins[plugin], repositories, plugin=True, priority_dev=link)
#             packages.append(PackageDependency(package=pkg, repository=repo))
#         
#         if target is not None:
#             for plugin in target.plugins:
#                 pkg, repo = _find_package(plugin, target.plugins[plugin], repositories, plugin=True, priority_dev=link)
#                 packages.append(PackageDependency(package=pkg, repository=repo))
    else:
        for package in name:
            s_name = package
            s_version = None
            s_repository = None
            
            chunks = package.split('@')
            if len(chunks)==2:
                try:
                    # check chunks[1] is a valid version range
                    VersionRange([])[chunks[1]]
                    s_name = chunks[0]
                    s_version = chunks[1]
                except Exception as e:
                    s_repository = chunks[0]
                    s_name = chunks[1]
            elif len(chunks)==3:
                s_repository = chunks[0]
                s_name = chunks[1]
                s_version = chunks[2]
            else:
                print(f"{package}: naming error", file=sys.stderr)
                exit(1)

            pkg, repo = _find_repository_package(repositories, s_name, version_range=s_version, repository=s_repository, editable=edit)
            packages.append(PackageDependency(package=pkg, repository=repo))

    # locate install folder
    if _global:
        path = os.path.expanduser(prefix_path("~/.army/dist/"))
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
            pkg, repo = _find_repository_package(repositories, dependency, version_range=package.dependencies[dependency], editable=edit)
            packages.append(PackageDependency(package=pkg, repository=repo, from_package=package))
# 
#         # append plugins to list
#         for plugin in package.plugins:
#             pkg, repo = _find_package(plugin, package.plugins[plugin], repositories, plugin=True, priority_dev=link)
#             dep_pkg = PackageDependency(package=pkg, repository=repo, from_package=package)
#             packages.append(dep_pkg)
# 
    # treat dependencies first
    dependencies.reverse()
 
    log.debug(f"packages: {dependencies}")

    # checks
    _check_dependency_version_conflict(dependencies)
#     _check_installed_version_conflict(dependencies)
     
    # clean dependency duplicates to avoid installing several times same package
    dependencies = _remove_duplicates(dependencies)
 
    # install
    for dependency in dependencies:
        install = False
        installed_package = load_installed_package(dependency.package.name, version_range=dependency.package.version)
        if installed_package:
            if force==True:
                print(f"reinstall {dependency.package}")
                install = True
            else:
                print(f"package {dependency.package} already installed", file=sys.stderr)
                install = False
        else:
            install = True
            print(f"install package {dependency.package}")
        
        try:
            if install==True:
                if edit==True and dependency.repository.editable==False:
                    print(f"{dependency.package.name}: repository is not editable", file=sys.stderr)
                install_path = os.path.join(path, dependency.package.name, str(dependency.package.version))
                if dependency.repository.editable==True:
                    dependency.package.install(path=install_path, edit=edit)
                else:
                    # link mode is only possible with editable repository
                    dependency.package.install(path=install_path, edit=False)
        except Exception as e:
            print_stack()
            print(f"{e}")
            exit(1)

def _find_repository_package(repositories, name, version_range="latest", repository=None, editable=None):
    package, repo = find_repository_package(repositories, name, version_range, repository, editable)

    if package is None:
        print(f"{name}: package not found", file=sys.stderr)
        exit(1)

    return package, repo

def _check_dependency_version_conflict(dependencies):
    """ Check if dependencies contains same package with version mismatch
    """
    # TODO: use VersionRange to true comparaison
    for dependency in dependencies:
        for dep in dependencies:
            if dep.package.name==dependency.package.name and dep.package.version!=dependency.package.version:
                msg = f"'{dependency.package.name}@{dependency.package.version}'"
                if dependency.from_package is None:
                    msg += f" from project"
                else:
                    msg += f" from '{dependency.from_package.name}'"
                msg += " conflicts with package "
                if dep.from_package is None:
                    msg += f"'{dep.package.name}@{dep.package.version}' from project"
                else:
                    msg += f"'{dep.package.name}@{dep.package.version}' from '{dep.from_package.name}'"
                print(msg, file=sys.stderr)
                exit(1)
 
# def _check_installed_version_conflict(dependencies):
#     """ Check if dependencies contains a package already installed with a version mismatch
#     """
#     installed = load_installed_packages(prefix=prefix)
#     for dependency in dependencies:
#         for inst in installed:
#             if inst.name==dependency.package.name and inst.version!=dependency.package.version:
#                 msg = f"'{dependency.package.name}@{dependency.package.version}'"
#                 if dependency.from_package is not None:
#                     msg += f" from '{dependency.from_package.name}'"
#                 msg += f" conflicts with installed package '{inst}'"
#                 print(msg, file=sys.stderr)
#                 exit(1)
             
     
 
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
