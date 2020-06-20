from army.api.log import log
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
from army.api.click import verbose_option 
from army.army import cli, packaging
import click
import os

from army.army import prefix

@packaging.command(name='package', help='Create versioned package')
@verbose_option()
@click.pass_context
def package(ctx, **kwargs):
    log.info(f"package")
    
    config = ctx.parent.config
    project = None
    if os.path.exists('army.toml'):
        try:
            # load project configuration
            project = load_project()
        except Exception as e:
            print_stack()
            log.debug(e)
    if project is None:
        log.info(f"no project loaded")

    print(project.name)
    
    file = project.package(os.getcwd(), 'output')
    