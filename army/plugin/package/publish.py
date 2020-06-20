from army.api.log import log
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
from army.api.click import verbose_option 
from army.army import cli, packaging
import click
import os
import keyring
import sys
from army.army import prefix

@packaging.command(name='publish', help='Publish versioned package')
@verbose_option()
@click.argument('name')
@click.pass_context
def publish(ctx, name, **kwargs):
    log.info(f"publish")
    
    config = ctx.parent.config

    # build repositories list
    repositories = load_repositories(config, prefix)

    repo = None
    for repository in repositories:
        if repository.name==name:
            repo = repository
    
    if repo is None:
        print(f"{name}: repository not found", file=sys.stderr)
        exit(1)

    try:
        service_id = f"army.{name}"
        user = keyring.get_password(service_id, 'user')
        if user is None:
            print(f"{name}: not logged to repository", file=sys.stderr)
            exit(1)
        password = keyring.get_password(service_id, user)
    except Exception as e:
        print_stack()
        log.debug(e)
        print(f"{name}: {e}", file=sys.stderr)
        exit(1)

    try:
        repo.login(user, password)
    except Exception as e:
        print_stack()
        log.debug(e)
        print(f"{name}: {e}", file=sys.stderr)
        exit(1)

    print("Not implemented")