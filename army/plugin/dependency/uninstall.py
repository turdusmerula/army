from army.api.log import log
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
from army import prefix
from army.api.click import verbose_option 
from army.api.package import load_installed_packages, load_installed_package
from army import cli, dependencies
import click
import os
import sys

@dependencies.command(name='uninstall', help='uninstall package')
@verbose_option()
# @click.option('--save', help='Update project package list', is_flag=True)    # TODO
@click.argument('name', nargs=-1)
@click.pass_context
def uninstall(ctx, name, **kwargs):
    log.info(f"uninstall {name} {kwargs}")
    
    config = ctx.parent.config

    if len(name)==0:
        print("nothing to uninstall", file=sys.stderr)
        exit(1)
        
    # build repositories list
    repositories = load_repositories(config, prefix)
    
    packages = []

    for package in name:
        pkg = load_installed_package(package, prefix=prefix)
        if pkg is None:
            print(f"{package}: package not installed", file=sys.stderr)
            exit(1)
        packages.append(pkg)
    
    for package in packages:
        package.uninstall()
    