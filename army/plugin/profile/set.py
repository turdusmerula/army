from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.log import log

@parser
@group(name="profile")
@command(name="profile")
@command(name='set', help='Set current profile')
@argument(name='name', count='*')
def profile_set(ctx, name, **kwargs):
    log.info(f"profile set")

