from army.api.log import log
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.army import prefix
from army.api.click import verbose_option 
from army.api.package import load_installed_packages
from army.army import cli
import click
import os

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
    