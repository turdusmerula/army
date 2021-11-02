from army.api.command import parser, group, command, option, argument
from army.api.console import ItemList
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
@option(name='all', shortcut='a', default=False, help='List all installed versions', flag=True)
@option(name='global', shortcut='g', default=False, help='List packages in user space', flag=True)
@option(name='local', shortcut='l', default=False, help='List packages inside project', flag=True)
def list(ctx, all, **kwargs):
    log.info(f"army list")
    
    scope = 'all'

    if 'global' in kwargs and kwargs['global']==True:  # not in parameters due to conflict with global keyword
        scope = 'global'
    if 'local' in kwargs and kwargs['local']==True:  # not in parameters due to conflict with global keyword
        if scope=='global':
            scope = 'all'
        else:
            scope = 'local'

    # load configuration
    config = ctx.config

    # load profile
    profile = ctx.profile
    
    output = ItemList(columns=['package', 'version', 'repository', 'scope', 'description'])
    
    packages = load_installed_packages(scope=scope, all=all, profile=profile)
    packages = sorted(packages, key=_compare_name_version)
    
    if len(packages)==0:
        print('no package found', file=sys.stderr)
        return

    for package in packages:
        output.add_line({
            'package': package.name,
            'version': package.version,
            'description': package.description,
            'repository': package.repository.name,
            'scope': package.scope
        })

    output.sort('package', 'version', 'scope')
    output.render()

def _compare_name_version(package):
    return ( package.name, package.version )
