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


@parser
@group(name="package")
@command(name='package', help='Create versioned package')
def package(ctx, **kwargs):
    log.info(f"package")
    
    config = ctx.config

    # load project
    project = ctx.project
    if project is None:
        print(f"no project loaded", file=sys.stderr)
        exit(1)

    try:    
        file = project.package(os.getcwd(), 'output')
    except Exception as e:
        print_stack()
        log.debug(e)
        print(f"packaging failed: {e}")
        exit(1)
        
    print(f"{os.path.relpath(file, os.getcwd())} generated")