from army.api.log import log
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
from army.api.click import verbose_option 
from army import cli, packaging
import click
import os

from army import prefix

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
        exit(1)

    try:    
        file = project.package(os.getcwd(), 'output')
    except Exception as e:
        print_stack()
        log.debug(e)
        print(f"packaging failed: {e}")
        exit(1)
        
    print(f"{os.path.relpath(file, os.getcwd())} generated")