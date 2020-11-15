from army.api.log import log
from army.api.debugtools import print_stack
from army.api.repository import load_repositories
from army.api.click import verbose_option 
from army import packaging
import click
import os
import sys
import getpass
import keyring

from army import prefix
from click.decorators import password_option

@packaging.command(name='login', help='Login to repository')
@verbose_option()
@click.option('-t', '--token', help='Login using a token', is_flag=True)
@click.argument('name')
@click.pass_context
def login(ctx, name, token, **kwargs):
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
    
    if token==True:
        token = getpass.getpass(prompt='token: ', stream=None) 
        try:
            repo.login(token=token)
        except Exception as e:
            print_stack()
            log.debug(e)
            print(f"{name}: {e}", file=sys.stderr)
            exit(1)
    else:
        user = input("login: ")
        password = getpass.getpass(prompt='password: ', stream=None) 
        
        try:
            repo.login(user=user, password=password)
        except Exception as e:
            print_stack()
            log.debug(e)
            print(f"{name}: {e}", file=sys.stderr)
            exit(1)

    print("logged in")
