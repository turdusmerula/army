from army.api.command import parser, group, command, option 
from army.api.console import ItemList
from army.api.debugtools import print_stack
from army.api.log import log
from army.api.project import load_project
from army.api.repository import load_repositories
import os

@parser
@group(name="repo")
@command(name="repo")
@command(name='list', help='List available repositories')
def list(ctx, **kwargs):
    log.info(f"army repo list")
    
    config = ctx.config
        
    # build repositories list
    repositories = load_repositories(config)
    if len(repositories)==0:
        print("no repository configured")
        return 

    output = ItemList(columns=['name', 'type', 'uri'])

    for r in repositories:
        output.add_line({
            'name': r.name,
            'type': r.type,
            'uri': r.uri
        })

    output.render()
