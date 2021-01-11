from army.api.command import parser, group, command, option 
from army.api.debugtools import print_stack
from army.api.log import log
from army.api.project import load_project
from army.api.repository import load_repositories
import os

@parser
@group(name="dependency")
@command(name='repos', help='List available repositories')
def repos(ctx, **kwargs):
    log.info(f"repos")
    
    config = ctx.parent.config
        
    # build repositories list
    repositories = load_repositories(config)
    if len(repositories)==0:
        print("no repository configured")
        return 
    
    column_name = ['name']
    column_type = ['type']
    column_uri = ['uri']

    for r in repositories:
        column_name.append(r.name)
        column_type.append(r.type)
        column_uri.append(r.uri)

    max_name = len(max(column_name, key=len))
    max_type = len(max(column_type, key=len))
    max_uri = len(max(column_uri, key=len))
  
    if len(column_name)>0:
        for i in range(len(column_name)):
            print(f"{column_name[i].ljust(max_name, ' ')} | ", end='')
            print(f"{column_type[i].ljust(max_type)} | ", end='')
            print(f"{column_uri[i].ljust(max_uri)}", end='')
            print()

# army_parser = get_army_parser()
# army_parser.dependency_group.add_command(name='repos', help='List available repositories', callback=repos)
