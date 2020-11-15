from army.api.log import log
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
from army.api.click import verbose_option 
from army import cli, packaging
import click
import os
import sys
import keyring.errors

from army import prefix

@packaging.command(name='logout', help='Logout from repository')
@verbose_option()
@click.argument('name')
@click.pass_context
def logout(ctx, name, **kwargs):
    log.info(f"logout {name}")
    
    config = ctx.parent.config
        
    # build repositories list
    repositories = load_repositories(config, prefix)
    
    repo = None
    for repository in repositories:
        if repository.name==name:
            repo = repository
    
    if repo is None:
        print(f"{name}: repository not found", file=sys.stderr)
        exit(1)
        
    service_id = f"army.{name}"
    
    try:
        repo.logout()
    except Exception as e:
        print_stack()
        log.debug(e)
        print(f"{name}: {e}", file=sys.stderr)
        exit(1)
    
    print("logged out")
        