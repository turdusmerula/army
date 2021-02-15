from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.log import log
from army.api.profile import load_profile, load_current_profile_cache
import sys

@parser
@group(name="profile")
@command(name="profile")
@command(name='current', help='Show current profile')
def profile_current(ctx, **kwargs):
    log.info(f"profile current")

    profile = None
    
    profiles = load_current_profile_cache()
    if len(profiles)==0:
        print("no profile set", file=sys.stderr)
        exit(1)
        
    for profile in profiles:
        print(profile)
