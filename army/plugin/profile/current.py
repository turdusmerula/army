from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.log import log


@parser
@group(name="profile")
@command(name="profile")
@command(name='current', help='Show current profile')
def profile_current(ctx, **kwargs):
    log.info(f"profile current")

