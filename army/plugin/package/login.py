from army.api.log import log
from army.api.debugtools import print_stack
from army.api.repository import load_repositories
from army.api.click import verbose_option 
from army.army import packaging
import click
import os
import sys
import getpass
import keyring

from army.army import prefix
from click.decorators import password_option

@packaging.command(name='login', help='Login to repository')
@verbose_option()
@click.argument('name')
@click.pass_context
def login(ctx, name, **kwargs):
    log.info(f"login {name}")
    
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
    
    user = input("login: ")
    password = getpass.getpass(prompt='password: ', stream=None) 
    
    try:
        repo.login(user, password)
    except Exception as e:
        print_stack()
        log.debug(e)
        print(f"{name}: {e}", file=sys.stderr)
        exit(1)

    service_id = f"army.{name}"
    
    # store password on keyring
    keyring.set_password(service_id, user, password)
    # store user on keyring
    keyring.set_password(service_id, 'user', user)

    print("logged in")
