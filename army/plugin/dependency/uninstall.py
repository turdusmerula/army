from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.dict_file import load_dict_file, save_dict_file
from army.api.log import log
from army.api.package import load_installed_package, find_repository_package
from army.api.repository import load_repositories, RepositoryPackage
from army.api.version import Version, VersionRange
import os
import sys

@parser
@group(name="dependency")
@command(name='uninstall', help='Uninstall package')
@option(name='global', shortcut='g', default=False, help='Uninstall package from user space', flag=True)
@argument(name='name', count='*')
def uninstall(ctx, name, **kwargs):
    log.info(f"uninstall {name} {kwargs}")

    if 'global' in kwargs and kwargs['global']==True:  # not in parameters due to conflict with global keyword
        scope = 'user'
    else:
        scope = 'local'

    # load configuration
    config = ctx.config

    if len(name)==0:
        print("nothing to uninstall", file=sys.stderr)
        exit(1)

    packages = []

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

        pkg = _find_installed_package(s_name, version=s_version, scope=scope)
        packages.append(pkg)

    pass
#     for package in name:
#         pkg = load_installed_package(package, prefix=prefix)
#         if pkg is None:
#             print(f"{package}: package not installed", file=sys.stderr)
#             exit(1)
#         packages.append(pkg)
#     
#     for package in packages:
#         package.uninstall()

def _find_installed_package(name, version, scope='user'):
    package, repo = load_installed_package(name, version, scope)

    if package is None:
        print(f"{name}: package not found", file=sys.stderr)
        exit(1)

    return package, repo
  