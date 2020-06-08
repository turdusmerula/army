from army.api.log import log
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
from army.army import cli
from army.api.click import verbose_option 
import click

from army.army import prefix

# TODO: implement multiple search criteria

@cli.command(name='search', help='Search package in repositories')
@verbose_option()
@click.argument('name')
@click.pass_context
def search(ctx, name, **kwargs):
    log.info(f"search {name}")
    
    # load configuration
    config = ctx.parent.config
    project_config = None
    try:
        # load project configuration
        project_config = load_project(config)
        config = project_config
    except Exception as e:
        print_stack()
        log.debug(e)
        log.info(f"no project loaded")

    log.debug(f"search {name}")
    
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
        column_repo.append(package.repository().name())
        column_package.append(package.name())
        column_version.append(str(package.version()))
        column_description.append(package.description())
  
    max_repo = len(max(column_repo, key=len))
    max_package = len(max(column_package, key=len))
    max_version = len(max(column_version, key=len))
  
    for i in range(len(column_repo)):
        print(f"{column_repo[i].ljust(max_repo, ' ')} | {column_package[i].ljust(max_package)} | {column_version[i].ljust(max_version)} | {column_description[i]}")
