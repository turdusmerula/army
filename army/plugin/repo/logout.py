from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.dict_file import load_dict_file, save_dict_file
from army.api.log import log
from army.api.package import find_repository_package
from army.api.path import prefix_path
from army.api.project import load_project
from army.api.repository import load_repositories, RepositoryPackage
from army.api.version import Version, VersionRange
import getpass
import keyring
import keyring.errors
import os
import sys

@parser
@group(name="repo")
@command(name="repo")
@command(name='logout', help='Logout from repository')
@argument('name')
def logout(ctx, name, **kwargs):
    log.info(f"logout {name}")
    
    config = ctx.config
        
    # build repositories list
    repositories = load_repositories(config)

    repo = None
    for repository in repositories:
        if repository.name==name:
            repo = repository
    
    if repo is None:
        print(f"{name}: repository not found", file=sys.stderr)
        exit(1)

    try:
        repo.load_credentials()
        repo.logout()
    except Exception as e:
        print_stack()
        log.debug(e)
        print(f"{name}: {e}", file=sys.stderr)
        exit(1)
    
    print("logged out")
        