from army.api.log import log
from army.api.debugtools import print_stack
from army.api.repository import load_repositories
from army.api.click import verbose_option 
from army import packaging
from army.plugin.profile.profile_group import profile
import click
import os
import sys
import getpass
import keyring

from army import prefix
from click.decorators import password_option

@profile.command(name='current', help='Show current profile')
@verbose_option()
@click.pass_context
def profile_current(ctx, **kwargs):
    log.info(f"profile current")
