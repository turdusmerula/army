from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.log import log
from army.api.profile import load_profile, load_current_profile_cache
import sys

@parser
@group(name="plugin2")
@command(name='command1', help='Command 1')
def plugin1_command1(ctx, **kwargs):
    print("plugin2_command1")
