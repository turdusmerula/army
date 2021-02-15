from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.log import log
from army.api.profile import load_profile, save_current_profile_cache

@parser
@group(name="profile")
@command(name="profile")
@command(name='set', help='Set current profile')
@argument(name="profiles", help="[PROFILE] ...", count='*')
def profile_set(ctx, profiles, **kwargs):
    log.info(f"profile set {' '.join(profiles)}")

    profile = None
    
    for name in profiles:
        profile = load_profile(name, profile)

    save_current_profile_cache(profiles)
