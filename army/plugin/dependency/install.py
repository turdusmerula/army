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
    def __init__(self, package, installed_by=None, installed_user=False):
        super(PackageDependency, self).__init__(data=package._data, repository=package.repository)
        self._installed_by = installed_by
        self._installed_user = installed_user
        
    @property
    def installed_by(self):
        return self._installed_by

    @property
    def installed_user(self):
        return self._installed_user

    def __repr__(self):
        return f"{self.repository.name}@{self.name}@{self.version}"

@parser
@group(name="dependency")
@command(name='install', help='Install package')
@option(name='edit', shortcut='e', default=False, help='Install packages from local repositories in edit mode', flag=True)
@option(name='global', shortcut='g', default=False, help='Install package in user space', flag=True)
@option(name='reinstall', shortcut='r', default=False, help='Force reinstall module if already exists', flag=True)
#@option(name='save', help='Update project package list', flag=True)    # TODO
@argument(name='name', help='PACKAGE ...', count='*')
def install(ctx, name, edit, reinstall, **kwargs):
    log.info(f"army install")
    # log.info(f"army install {name} --edit={edit} --reinstall={reinstall} --global={kwargs['global']}")
    
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

    # load profile
    profile = ctx.profile
    
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
            packages.append(PackageDependency(package=pkg, installed_user=True))
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
            elif len(chunks)!=1:
                print(f"{package}: naming error", file=sys.stderr)
                exit(1)

            pkg, repo = _find_repository_package(repositories, s_name, version_range=s_version, repository=s_repository, editable=edit)
            packages.append(PackageDependency(package=pkg, installed_user=True))
     
    # build dependencies tree
    dependency_tree = _build_dependency_tree(repositories, packages, editable=edit)
    
    # checks
    result = True
    if _check_dependency_version_conflict(dependency_tree)==False:
        result = False
#     if _check_installed_version_conflict(dependency_tree)==False:
#         result = False
    
    if result==False:
        print("install failed", file=sys.stderr)
        exit(1)
    
    _install_packages(repositories, dependency_tree, edit=edit, scope=scope, reinstall=reinstall, profile=profile)
    
    print("install finished ok")
    
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
        if version_range is None:
            print(f"{name}: package not found", file=sys.stderr)
        else:
            print(f"{name}@{version_range}: package not found", file=sys.stderr)
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

def _install_packages(repositories, dependency_tree, edit=False, scope='local', reinstall=False, profile=None):
    _resursive_install_packages(repositories, dependency_tree, level=0, edit=edit, scope=scope, reinstall=reinstall, profile=profile)

def _resursive_install_packages(repositories, dependency_tree, level, edit, scope, reinstall, profile):
    tab = ""
    for l in range(0, level):
        tab += "  "

    for dependency in dependency_tree:
        package = dependency_tree[dependency]['package']
        dependencies = dependency_tree[dependency]['dependencies']

        if len(dependencies)>0:
            print(f'{tab}{package}')
            
        _resursive_install_packages(repositories, dependencies, level=level+1, edit=edit, scope=scope, reinstall=reinstall, profile=profile)

        _install_package(package, level=level, edit=edit, scope=scope, reinstall=reinstall, profile=profile)

def _install_package(package, level, edit, scope, reinstall, profile):
    tab = ""
    for l in range(0, level):
        tab += "  "

    # locate install folder
    if scope=='local':
        path = ""
    else:
        path = os.path.expanduser(prefix_path("~/.army/"))

    try:
        # search package in installed packages
        installed_package = load_installed_package(package.name, version_range=package.version, scope=scope, exist_ok=True, profile=profile)
    except Exception as e:
        print(f"Error loading package {package}", file=sys.stderr)
        print("install failed", file=sys.stderr)
        exit(1)

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
            print(f' already installed, skip')
 
    try:
        install_path = os.path.join(path, 'dist', package.name, str(package.version))

        if install==True:
            if edit==True and package.repository.editable==False:
                # edit mode is only possible with editable repository
                print(f"{package}: repository is not editable", file=sys.stderr)
                edit = False
                
            package.install(path=path, force=reinstall, edit=edit)

        content = load_dict_file(install_path, "army")
        if package.installed_by is not None:
            name = f"{package.installed_by.name}@{package.installed_by.version}"
            if 'installed_by' not in content:
                content['installed_by'] = [name]
            elif name not in content['installed_by']:
                content['installed_by'].append(name)
        if package.installed_user==True:
            content['installed_user'] = True
        save_dict_file(install_path, "army", content)
            
    except Exception as e:
        print_stack()
        print(f"{e}")
        exit(1)

