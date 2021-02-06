from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.log import log
from army.api.profile import load_profile, load_current_profile_cache
import sys

@parser
@group(name="plugin1")
@command(name='command2', help='Command 2')
def plugin1_command2(ctx, **kwargs):
    print("plugin1_command2")
