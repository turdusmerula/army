from army.api.log import log
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.army import prefix
from army.api.click import verbose_option 
from army.api.package import load_installed_packages
from army.army import cli
import click
import sys


@cli.command(name='init', help='Create a new project')
@verbose_option()
@click.pass_context
def init(ctx, **kwargs):
    log.info(f"init")
    
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

    print("Not yet implemented")
