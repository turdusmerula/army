from army.api.log import log
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
from army.api.click import verbose_option 
from army import cli, dependencies
import click
import os
import sys
from army import prefix

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
        try:
            r.update()
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            print(f"{r.name}: {e}", file=sys.stderr)
    print("updated")