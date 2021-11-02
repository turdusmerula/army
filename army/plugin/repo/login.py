from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.dict_file import load_dict_file, save_dict_file
from army.api.log import log
from army.api.package import find_repository_package
from army.api.path import prefix_path
from army.api.project import load_project
from army.api.repository import load_repositories, RepositoryPackage
from army.api.version import Version, VersionRange
import getpass
import keyring
import os
import sys

@parser
@group(name="repo")
@command(name="repo")
@command(name='login', help='Login to repository')
@option(shortcut='t', name='token', value="TOKEN", help='Login token', flag=True, default=None)
@option(shortcut='u', name='user', value="USER", help='Login user', flag=True, default=None)
@option(shortcut='p', name='password', value="PASSWORD", help='Login password', flag=True, default=None)
@argument('name')
def login(ctx, name, token, user, password, **kwargs):
    log.info(f"army repo login")
    
    config = ctx.config
        
    # build repositories list
    repositories = load_repositories(config)
    
    repo = None
    for repository in repositories:
        if repository.name==name:
            repo = repository
    
    if repo is None:
        print(f"{name}: repository not found", file=sys.stderr)
        exit(1)

    if len(repo.Login)==0:
        print("unauthentified repository")
    
    methods = []
    for method in repo.Login:
        methods.append(method.Method)
    
    if token is not None and user is not None:
        print("Can not combine user and token login", file=sys.stderr)
        exit(1)

    method = None
    if token is not None:
        method = 'token'
    if user is not None:
        method = 'user-password'

    if method is None:
        if len(repo.Login)==1:
            method = repo.Login[0].Method
        elif len(repo.Login)>1:
            method = input(f"authentification method ({', '.join(methods)}): ")
            if method not in methods:
                print(f"{method}: unhandled authentification method", file=sys.stderr)
                exit(1)
    else:
        if method not in methods:
            print(f"{method}: unsupported authentification method for repository", file=sys.stderr)
            exit(1)
    
    logged = False
    
    if method=='token':
        if token is None:
            token = getpass.getpass(prompt='token: ', stream=None) 
        
        try:
            repo.login(token=token)
            logged = True
        except Exception as e:
            print_stack()
            log.debug(e)
            print(f"{name}: {e}", file=sys.stderr)
            exit(1)
            
    elif method=='user-password':
        if user is None:
            user = input("login: ")
        if password is None:
            password = getpass.getpass(prompt='password: ', stream=None) 
        
        try:
            repo.login(user=user, password=password)
            logged = True
        except Exception as e:
            print_stack()
            log.debug(e)
            print(f"{name}: {e}", file=sys.stderr)
            exit(1)
                
    if logged==True:
        print("logged in")
    else:
        print("Login failed")
