from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.dict_file import load_dict_file, save_dict_file
from army.api.log import log
from army.api.package import load_installed_package, find_repository_package, InstalledPackage, parse_package_name
from army.api.repository import load_repositories, RepositoryPackage
from army.api.version import Version, VersionRange
import os
import sys

loaded_packages = {}

class UninstalledPackage(InstalledPackage):
    def __init__(self, package):
        super(UninstalledPackage, self).__init__(data=package._data, path=package.path, profile=None)
        self._direct_uninstall = False
        self._uninstall = False
        
    def __repr__(self):
        return f"{self.repository.name}@{self.name}@{self.version}"

@parser
@group(name="dependency")
@command(name='uninstall', help='Uninstall package')
@option(name='global', shortcut='g', default=False, help='Uninstall package from user space', flag=True)
@option(name='yes', shortcut='y', default=False, help="don't ask for confirmation", flag=True)
@argument(name='name', count='*')
def uninstall(ctx, name, yes, **kwargs):
    log.info(f"army uninstall")

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
        print("nothing to uninstall", file=sys.stderr)
        exit(1)

    # load profile
    profile = ctx.profile

    tree = {}
    
    packages = []
    
    if len(name)==0:
        for package, version in project.dependencies.items():
            packages.append(_find_installed_package(package, version=version, scope=scope, profile=profile))

    else:
        for package in name:
            s_name = package
            s_version = None
            
            chunks = package.split('@')
            if len(chunks)==2:
                try:
                    # check chunks[1] is a version range
                    Version(chunks[1])
                    s_name = chunks[0]
                    s_version = chunks[1]
                except Exception as e:
                    print(f"{package}: naming error", file=sys.stderr)
                    exit(1)
            elif len(chunks)!=1:
                print(f"{package}: naming error", file=sys.stderr)
                exit(1)
            
            packages.append(_find_installed_package(s_name, version=s_version, scope=scope, profile=profile))
    
    for pkg in packages:
        pkg['package']._direct_uninstall = True
    
        parents = _get_top_level_parents(pkg['package'], scope)
        for parent in parents:
            tree[parent] = parents[parent]
            tree[parent]['package']._direct_uninstall = True
    
        if len(parents)==0:
            package_ref = f"{scope}@{pkg['package'].name}@{pkg['package'].version}"
            tree[package_ref] = pkg

    def print_tree(tree, tab=''):
        for item in tree:
            package = tree[item]['package']
            print(f"{tab}{item} [installed_user={package.installed_user}, installed_by={package.installed_by}, uninstall={package._uninstall}, direct_uninstall={package._direct_uninstall}]")
            print_tree(tree[item]['dependencies'], f"{tab}  ")
    
#     print("++++")
#     print_tree(tree)

    _update_tree(tree)
    
#     print("++++")
#     print_tree(tree)
#     print("++++")
    
    to_uninstall = _get_remove_list(tree)
    
    if yes==False:
        if len(to_uninstall)>1:
            print("The following packages will be removed:")
        else:
            print("The following package will be removed:")
            
        print("\t", end='')
        for pkg in sorted(to_uninstall):
            print(pkg, "", end="")
        print("")
        print("Do you want to continue? [Y/n] ", end="")
        res = input()
        if res!='y' and res!='Y':
            exit(0)
    
    for package_id in to_uninstall:
        print(f"uninstall {package_id}")
        package = to_uninstall[package_id]['package']
        package.uninstall()
        if len(os.listdir(os.path.dirname(package.path)))==0:
            os.rmdir(os.path.dirname(package.path))
    
    print("uninstalled ok")

def _get_top_level_parents(package, scope):
    parents = {}
    
    _recursive_get_top_level_parents(package, scope, parents)
    
    return parents

def _recursive_get_top_level_parents(package, scope, parents):
    for parent in package.installed_by:
        parent_ref = parse_package_name(parent)
        parent_name = parent_ref['name']
        parent_version = parent_ref['version']

        parent_id = f"{scope}@{parent_name}@{parent_version}"
        if parent_id not in parents:
            parents[parent_id] = _find_installed_package(parent_name, parent_version, scope)
            _recursive_get_top_level_parents(parents[parent_id]['package'], scope, parents)

def _find_installed_package(name, version, scope='user', from_package=None, profile=None):
    global loaded_packages
    
    package = load_installed_package(name, version, scope)
    if package is None:
        package = load_installed_package(name, version_range=None, scope=scope, profile=profile)
        if from_package is None:
            if package is None or version is None:
                print(f"{name}: package not installed", file=sys.stderr)
            else:
                print(f"{name}: no version matching '{version}' installed", file=sys.stderr)
        else:
            if package is None or version is None:
                print(f"{name}: dependency from {from_package} not installed", file=sys.stderr)
            else:
                print(f"{name}: dependency matching '{version}' from {from_package} not installed", file=sys.stderr)
        exit(1)
    
    package = UninstalledPackage(package)

    pakage_id = f"{scope}@{package.name}@{package.version}"
    
    if pakage_id in loaded_packages:
        return loaded_packages[pakage_id]
    else:
        loaded_packages[pakage_id] = {
            'package': package,
            'dependencies': {}
        }
        loaded_packages[pakage_id]['dependencies'] = _load_package_dependency_tree(package, scope)

    return loaded_packages[pakage_id]

def _load_package_dependency_tree(package, scope):
    tree = {}
    for dependency in package.dependencies:
        # TODO add dependency name splitter
        dependency_ref = parse_package_name(dependency)
        dependency_name = dependency_ref['name']
        dependency_version = dependency_ref['version']
        
        pkg = _find_installed_package(dependency_name, version=dependency_version, scope=scope, from_package=package)
        if pkg is None:
            print(f"{dependency}: package not found, dependency tree may be corrupt", file=sys.stderr)
            exit(1)
        
        dependency_id = f"{scope}@{pkg['package'].name}@{pkg['package'].version}"
        tree[dependency_id] = {
            'package': pkg['package'],
            'dependencies': _load_package_dependency_tree(pkg['package'], scope=scope)
        }
    
    return tree

def _update_tree(tree):
    while _recursive_update_tree(tree)==True:
        continue
    
def _recursive_update_tree(tree):
    changed = False
    
    for package_id in tree:
        package = tree[package_id]['package']
        dependencies = tree[package_id]['dependencies']
    
        if package._uninstall==False:
            if package._direct_uninstall==True:
                package._uninstall = True
                changed = True
                
            if len(package.installed_by)==0 and package.installed_user==False:
                package._uninstall = True                
                changed = True

        if package._uninstall==True:
            package_ref = f"{package.name}@{package.version}"
            for dependency_id in dependencies:
                dependency = dependencies[dependency_id]['package']
                
                if package_ref in dependency.installed_by:
                    dependency.remove_installed_by(package_ref)

        if _recursive_update_tree(dependencies)==True:
            changed = True
    
    return changed

def _get_remove_list(tree):
    res = {}
    _recursive_get_remove_list(tree, res)
    return res

def _recursive_get_remove_list(tree, package_list):

    for package_id in tree:
        package = tree[package_id]['package']
        package_ref = f"{package.name}@{package.version}"
        if package_ref not in package_list and package._uninstall==True:
            package_list[package_ref] = tree[package_id]
    
        _recursive_get_remove_list(tree[package_id]['dependencies'], package_list)
    