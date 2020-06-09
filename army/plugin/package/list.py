from army.api.log import log
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.army import prefix
from army.api.click import verbose_option 
from army.api.package import load_installed_packages
from army.army import cli
import click
import sys

class PackageDependency(object):
    def __init__(self, package, from_package=None):
        self._package = package
        self._from_package = from_package
    
    def package(self):
        return self._package
    
    def from_package(self):
        return self._from_package
    
@cli.command(name='list', help='List installed packages')
@verbose_option()
@click.pass_context
def list(ctx, **kwargs):
    log.info(f"list")
    
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

    packages = load_installed_packages()

    if len(packages)==0:
        print('no package found', file=sys.stderr)
        return
 
    column_package = ['package']
    column_version = ['version']
    column_description = ['description']
    column_repo = ['repository']
#
    for package in packages:
        column_package.append(package.name)
        column_version.append(str(package.version))
        column_description.append(package.description)
        column_repo.append(package.repository.name)
  
    max_package = len(max(column_package, key=len))
    max_version = len(max(column_version, key=len))
    max_description = len(max(column_description, key=len))
    max_repo = len(max(column_repo, key=len))
  
    for i in range(len(column_repo)):
        print(f"{column_package[i].ljust(max_package)} | ", end='')
        print(f"{column_version[i].ljust(max_version)} | ", end='')
        print(f"{column_description[i].ljust(max_description)} | ", end='')
        print(f"{column_repo[i].ljust(max_repo, ' ')}", end='')
        print()
