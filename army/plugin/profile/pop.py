from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.log import log
from army.api.profile import load_profile, load_current_profile_cache, save_current_profile_cache
import sys

@parser
@group(name="profile")
@command(name="profile")
@command(name='pop', help='Pop profile from current profile')
def profile_pop(ctx, **kwargs):
    log.info(f"profile pop")

    profile = None
    profiles = load_current_profile_cache()
    name = profiles.pop()
    
    print(f"removed: {name}")
    
    save_current_profile_cache(profiles)
