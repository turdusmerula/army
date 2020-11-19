from army.api.log import log
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
from army.api.click import verbose_option 
from army import cli, packaging
import click
import os
import keyring
import sys
from army import prefix

@packaging.command(name='publish', help='Publish versioned package')
@verbose_option()
@click.option('-f', '--force', help='Force create release if already exists', is_flag=True)
@click.argument('name')
@click.pass_context
def publish(ctx, name, force, **kwargs):
    log.info(f"publish")
    
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

    # build repositories list
    repositories = load_repositories(config, prefix)

    repo = None
    for repository in repositories:
        if repository.name==name:
            repo = repository
    
    if repo is None:
        print(f"{name}: repository not found", file=sys.stderr)
        exit(1)

    if repo.load_credentials()==False:
        print(f"{name}: no credentials found", file=sys.stderr)
        exit(1)

    
    # package
    try:    
        file = project.package(os.getcwd(), 'output')
        print(f"{os.path.relpath(file, os.getcwd())} generated")
    except Exception as e:
        print_stack()
        log.debug(e)
        print(f"packaging failed: {e}")
        exit(1)

    # TODO check version is tagged and files are commited and pushed

    # publish
    try:
        repo.publish(project, file, overwrite=force)
    except Exception as e:
        print_stack()
        log.debug(e)
        print(f"publishing failed: {e}")
        exit(1)

    print(f"{os.path.relpath(file, os.getcwd())} published")
