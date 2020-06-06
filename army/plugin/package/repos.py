from army.api.log import log
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
from army.api.click import verbose_option 
from army.army import cli
import click
import os

from army.army import prefix

@cli.command(name='repos', help='List available repositories')
@verbose_option()
@click.pass_context
def repos(ctx, **kwargs):
    log.info(f"repos")
    
    config = ctx.parent.config
    
    project_config = None
    try:
        # load project configuration
        project_config = load_project(config)
    except Exception as e:
        log.debug(f"no project loaded")
        project_config = config
    
    # build repositories list
    repositories = load_repositories(project_config, prefix)
    if len(repositories)==0:
        print("no repository configured")
        return 
    
    column_name = ['name']
    column_type = ['type']
    column_uri = ['uri']

    for r in repositories:
        column_name.append(r.name())
        column_type.append(r.type())
        column_uri.append(r.uri())

    max_name = len(max(column_name, key=len))
    max_type = len(max(column_type, key=len))
    max_uri = len(max(column_uri, key=len))
  
    if len(column_name)>0:
        for i in range(len(column_name)):
            print(f"{column_name[i].ljust(max_name, ' ')} | {column_type[i].ljust(max_type)} | {column_uri[i].ljust(max_uri)}")
