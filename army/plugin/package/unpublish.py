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
@command(name='unpublish', help='Unpublish versioned package')
@argument('repo_name', help='REPOSITORY')
def publish(ctx, repo_name, **kwargs):
    log.info(f"army unpublish")
    
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
        if repository.name==repo_name:
            repo = repository
    
    if repo is None:
        print(f"{repo_name}: repository not found", file=sys.stderr)
        exit(1)

    # if repo.load_credentials()==False:
    #     print(f"{repo_name}: no credentials found", file=sys.stderr)
    #     exit(1)

    # unpublish
    try:
        repo.unpublish(project)
    except Exception as e:
        print_stack()
        log.debug(e)
        print(f"unpublishing failed: {e}")
        exit(1)

    print(f"{project} unpublished")
