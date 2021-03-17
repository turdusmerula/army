from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.dict_file import load_dict_file, save_dict_file
from army.api.log import log
from army.api.package import load_installed_package, find_repository_package
from army.api.path import prefix_path
from army.api.project import load_project
from army.api.repository import load_repositories, RepositoryPackage
from army.api.version import Version, VersionRange
import os
import sys

class PackageDependency(RepositoryPackage):
    def __init__(self, package, installed_by=None):
        super(PackageDependency, self).__init__(data=package._data, repository=package.repository)
        self._installed_by = installed_by
        
    @property
    def installed_by(self):
        return self._installed_by

#     def _install_edit_project_file(self, path, content):
#         super(PackageDependency, self)._install_edit_project_file(path, content)
#         
#         # add package owners
#         if str(self._installed_by) not in content['installed_by']:
#             content['installed_by'].append(str(self._installed_by))
 
#     def install(self, path, edit=False):
#         super(PackageDependency, self)._preinstall(path=path, edit=edit)
#         super(PackageDependency, self)._install(path=path, edit=edit)
# 
#         # add repository informations installed package
#         try:
#             self._copy(os.path.join(self._source_path, "army.yaml"), dest)
#             content = load_dict_file(self._source_path, "army")
#             # add packseldage install source
#             content['repository'] = {
#                 'uri': str(self._repository._uri),
#                 'name': self._repository._name
#                 }
#             # add package owners
#             content['parents'] = self._parents
#             
#             save_dict_file(dest, "army", content)
#         except Exception as e:
#             print_stack()
#             log.debug(e)
# 
#         super(PackageDependency, self)._postinstall(path=path, edit=edit)

    def __repr__(self):
        return f"{self.repository.name}@{self.name}@{self.version}"

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
    
    if 'global' in kwargs and kwargs['global']==True:  # not in parameters due to conflict with global keyword
        scope = 'user'
    else:
        scope = 'local'
        
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
        try:
            repository.load_credentials()
        except Exception as e:
            print_stack()
            log.error(f"{e}")
         
    packages = []
 
    if len(name)==0:
#         # get target config
#         target = ctx.target
#         if target is None:
#             print(f"no target specified", file=sys.stderr)
#             exit(1)

        for package, version in project.dependencies.items():
            pkg, repo = _find_repository_package(repositories, package, version_range=version, editable=edit)
            packages.append(PackageDependency(package=pkg))

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
            packages.append(PackageDependency(package=pkg))
     
    # build dependencies tree
    dependency_tree = _build_dependency_tree(repositories, packages, editable=edit)
    
    # checks
    result = True
    if _check_dependency_version_conflict(dependency_tree)==False:
        result = False
#     if _check_installed_version_conflict(dependency_tree)==False:
#         result = False
    
    if result==False:
        exit(1)
    
    _install_packages(repositories, dependency_tree, edit=edit, scope=scope, reinstall=reinstall)
    
#     dependencies = []
#     while(len(packages)>0):
#         # get dependencies from top level package to end level
#         package_dep = packages.pop(0)
#         package = package_dep.package
#  
#         # dependency treated ok, append to list
#         dependencies.append(package_dep)
#          
#         # append dependencies to list
#         for dependency in package.dependencies:
#             pkg, repo = _find_repository_package(repositories, dependency, version_range=package.dependencies[dependency], editable=edit)
#             packages.append(PackageDependency(package=pkg, repository=repo, from_package=package))
# # 
# #         # append plugins to list
# #         for plugin in package.plugins:
# #             pkg, repo = _find_package(plugin, package.plugins[plugin], repositories, plugin=True, priority_dev=link)
# #             dep_pkg = PackageDependency(package=pkg, repository=repo, from_package=package)
# #             packages.append(dep_pkg)
# # 
#     # treat dependencies first
#     dependencies.reverse()
#  
#     log.debug(f"packages: {dependencies}")
# 
#     # checks
#     _check_dependency_version_conflict(dependencies)
# #     _check_installed_version_conflict(dependencies)
#      
#     # clean dependency duplicates to avoid installing several times same package
#     dependencies = _remove_duplicates(dependencies)
#  
#     # install
#     for dependency in dependencies:
#         _install_package(dependency)

def _build_dependency_tree(repositories, packages, editable=False):
    tree = {}
    
    for package in packages:
        dependencies = _find_dependencies(repositories, package, editable=editable)
        tree[package.name] = {
            'package': package,
            'dependencies': _build_dependency_tree(repositories, dependencies, editable=False)
        }

    return tree

def _find_dependencies(repositories, package, editable=False):
    dependencies = []
    for name, version in package.dependencies.items():
        pkg, repo = find_repository_package(repositories, name, version_range=version, editable=editable)
        if pkg is None:
            print(f"{name}: dependency from {package} not found", file=sys.stderr)
            exit(1)
        
        dependencies.append(PackageDependency(package=pkg, installed_by=package))
    return dependencies

def _find_repository_package(repositories, name, version_range="latest", repository=None, editable=None):
    package, repo = find_repository_package(repositories, name, version_range, repository, editable)

    if package is None:
        print(f"{name}: package not found", file=sys.stderr)
        exit(1)

    return package, repo


def _check_dependency_version_conflict(dependency_tree):
    """ Check if dependencies contains same package with version mismatch
    """
    
    packages = {}
    return _recursive_check_dependency_version_conflict(dependency_tree, packages)
    

def _recursive_check_dependency_version_conflict(dependency_tree, packages):
    
    result = True
    
    for dependency in dependency_tree:
        package = dependency_tree[dependency]['package']
        dependencies = dependency_tree[dependency]['dependencies']
        
        if package.name in packages:
            if package.version!=packages[package.name].version:
                uppkg = packages[package.name]
                downpkg = package
                
                print("version mismatch: ", end='', file=sys.stderr)
                print(f"{uppkg}", end='', file=sys.stderr)
                if uppkg.installed_by is not None:
                    print(f" from {uppkg.installed_by}", end='', file=sys.stderr)
                print(" conflicts with package", end='', file=sys.stderr)
                if downpkg.installed_by is None:
                    print(f" {downpkg}", end='', file=sys.stderr)
                else:
                    print(f" {downpkg}' from {downpkg.installed_by}", end='', file=sys.stderr)
                print("", file=sys.stderr)
                result = False

        packages[package.name] = package
        
        if _recursive_check_dependency_version_conflict(dependencies, packages)==False:
            result = False
    
    return result

# def _check_installed_version_conflict(dependency_tree):
#     """ Check if dependencies contains same package with version mismatch
#     """
#     
#     packages = {}
#     return _recursive_check_dependency_version_conflict(dependency_tree, packages)
# 
# def _recursive_check_installed_version_conflict(dependency_tree, packages):
#     result = True
#     return result

 
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

def _install_packages(repositories, dependency_tree, edit=False, scope='local', reinstall=False):
    _resursive_install_packages(repositories, dependency_tree, level=0, edit=edit, scope=scope, reinstall=reinstall)

def _resursive_install_packages(repositories, dependency_tree, level, edit, scope, reinstall):
    for dependency in dependency_tree:
        package = dependency_tree[dependency]['package']
        dependencies = dependency_tree[dependency]['dependencies']
        
        _resursive_install_packages(repositories, dependencies, level=level+1, edit=edit, scope=scope, reinstall=reinstall)

        _install_package(package, level=level, edit=edit, scope=scope, reinstall=reinstall)

def _install_package(package, level, edit, scope, reinstall):
    tab = ""
    for l in range(0, level):
        tab += "  "

    # locate install folder
    if scope=='local':
        path = "dist"
    else:
        path = os.path.expanduser(prefix_path("~/.army/dist/"))

    # search package in installed packages
    installed_package = load_installed_package(package.name, version_range=package.version, scope=scope)

    install = False
     
    print(f'{tab}{package}', end='')
    if installed_package is None:
        install = True
        print(f' install')
    else:
        if reinstall==True:
            print(f' reinstall')
            install = True
        else:
            print(f' installed, skip')
 
    try:
        install_path = os.path.join(path, package.name, str(package.version))

        if install==True:
            if edit==True and package.repository.editable==False:
                # edit mode is only possible with editable repository
                print(f"{package}: repository is not editable", file=sys.stderr)
                edit = False
                
            package.install(path=install_path, edit=edit)

        if package.installed_by is not None:
            content = load_dict_file(install_path, "army")
            name = f"{package.installed_by.name}@{package.installed_by.version}"
            if 'installed_by' not in content:
                content['installed_by'] = [name]
            elif name not in content['installed_by']:
                content['installed_by'].append(name)
            save_dict_file(install_path, "army", content)

    except Exception as e:
        print_stack()
        print(f"{e}")
        exit(1)

