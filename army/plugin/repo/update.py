from army.api.command import parser, group, command, option, argument
from army.api.log import log
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
import os
import sys

@parser
@group("repo")
@command("repo")
@command(name='update', help='Update repository indexes')
def update(ctx, **kwargs):
    log.info(f"army repo update")
    
    config = ctx.config
        
    # build repositories list
    repositories = load_repositories(config)
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
