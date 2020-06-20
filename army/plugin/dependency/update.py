from army.api.log import log
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
from army.api.click import verbose_option 
from army.army import cli, dependencies
import click
import os

from army.army import prefix

@dependencies.command(name='update', help='Update repository indexes')
@verbose_option()
@click.pass_context
def update(ctx, **kwargs):
    log.info(f"update")
    
    config = ctx.parent.config
        
    # build repositories list
    repositories = load_repositories(config, prefix)
    if len(repositories)==0:
        print("no repository configured")
        return 
    
    for r in repositories:
        print(f"update {r.name}")
        r.update()