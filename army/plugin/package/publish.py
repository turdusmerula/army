from army.api.command import parser, group, command, option, argument
from army.api.log import log
from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
import os
import keyring
import sys

@parser
@group(name="package")
@command(name='publish', help='Publish versioned package')
@option(shortcut='f', name='force', help='Force create release if already exists', flag=True, default=False)
@argument('name')
def publish(ctx, name, force, **kwargs):
    log.info(f"publish")
    
    config = ctx.config

    # load project
    project = ctx.project
    if project is None:
        print(f"no project loaded", file=sys.stderr)
        exit(1)

    # build repositories list
    repositories = load_repositories(config)

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
