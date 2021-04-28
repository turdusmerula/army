from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.dict_file import load_dict_file, save_dict_file
from army.api.log import log
from army.api.package import load_installed_packages
from army.api.path import prefix_path
from army.api.project import load_project
from army.api.repository import load_repositories, RepositoryPackage
from army.api.version import Version, VersionRange
import os
import sys

@parser
@group(name="dependency")
@command(name='list', help='List installed packages')
@option(name='global', shortcut='g', default=False, help='List packages in user space', flag=True)
@option(name='all', shortcut='a', default=False, help='List all installed versions', flag=True)
def list(ctx, all, **kwargs):
    log.info(f"list")
    
    if 'global' in kwargs and kwargs['global']==True:  # not in parameters due to conflict with global keyword
        scope = 'user'
    else:
        scope = 'local'

    # load configuration
    config = ctx.config

    packages = load_installed_packages(scope=scope, all=all)
    packages = sorted(packages, key=_compare_name_version)
    
    if len(packages)==0:
        print('no package found', file=sys.stderr)
        return
 
    column_package = ['package']
    column_version = ['version']
    column_description = ['description']
    column_repo = ['repository']
#
    for package in packages:
        column_package.append(package.name)
        column_version.append(str(package.version))
        column_description.append(package.description)
        column_repo.append(package.repository.name)
  
    max_package = len(max(column_package, key=len))
    max_version = len(max(column_version, key=len))
    max_description = len(max(column_description, key=len))
    max_repo = len(max(column_repo, key=len))
  
    for i in range(len(column_repo)):
        print(f"{column_package[i].ljust(max_package)} | ", end='')
        print(f"{column_version[i].ljust(max_version)} | ", end='')
        print(f"{column_description[i].ljust(max_description)} | ", end='')
        print(f"{column_repo[i].ljust(max_repo, ' ')}", end='')
        print()

def _compare_name_version(package):
    return ( package.name, package.version )
