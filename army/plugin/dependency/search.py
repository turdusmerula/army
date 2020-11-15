from army.api.log import log
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
from army import cli, dependencies
from army.api.click import verbose_option 
import click
import os
from army import prefix

# TODO: implement multiple search criteria

@dependencies.command(name='search', help='Search package in repositories')
@verbose_option()
@click.argument('name')
@click.pass_context
def search(ctx, name, **kwargs):
    log.info(f"search {name}")
    
    # load configuration
    config = ctx.parent.config
    
    # build repositories list
    repositories = load_repositories(config, prefix)
    packages = []
     
    for r in repositories:
        res = r.search(name)
        if len(res)>0:
            for pkg in res:
                packages.append(res[pkg])

    if len(packages)==0:
        print(f'No matches found for "{name}"')
        return
 
    column_repo = ['repository']
    column_package = ['package']
    column_version = ['version']
    column_description = ['description']
#
    for package in packages:
        column_repo.append(package.repository.name)
        column_package.append(package.name)
        column_version.append(str(package.version))
        column_description.append(package.description)
  
    max_repo = len(max(column_repo, key=len))
    max_package = len(max(column_package, key=len))
    max_version = len(max(column_version, key=len))
    max_description = len(max(column_description, key=len))
  
    for i in range(len(column_repo)):
        print(f"{column_repo[i].ljust(max_repo, ' ')} | ", end='')
        print(f"{column_package[i].ljust(max_package)} | ", end='')
        print(f"{column_version[i].ljust(max_version)} | ", end='')
        print(f"{column_description[i].ljust(max_version)}", end='')
        print()