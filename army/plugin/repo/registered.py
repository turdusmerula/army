from army.api.command import parser, group, command, option 
from army.api.console import ItemList
from army.api.debugtools import print_stack
from army.api.log import log
from army.api.project import load_project
from army.api.repository import repository_types, IndexedRepository
import os

@parser
@group(name="repo")
@command(name="repo")
@command(name='registered', help='List registered repository ')
def registered(ctx, **kwargs):
    log.info(f"army repo registered")
    
    config = ctx.config
        
    # build repository types list
    if len(repository_types)==0:
        print("no repository registered")
        return 

    output = ItemList(columns=['name', 'attributes'])

    for r in repository_types:
        attributes = []
        if repository_types[r].Editable:
            attributes.append('editable')
        if issubclass(repository_types[r], IndexedRepository):
            attributes.append('indexed')
        output.add_line({
            'name': repository_types[r].Type,
            'attributes': ', '.join(attributes)
        })

    output.sort('name')
    output.render()
