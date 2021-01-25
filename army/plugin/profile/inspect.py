from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.log import log
from army.api.profile import load_profile_list, load_profile
#import oyaml as yaml
import yaml

@parser
@group(name="profile")
@command(name="profile")
@command(name='inspect', help='Inspect profile')
@argument(name="profiles", help="[PROFILE] ...", count='*')
def profile_current(ctx, profiles, **kwargs):
    log.info(f"profile inspect {' '.join(profiles)}")
    
    profile = None
    
    for name in profiles:
        profile = load_profile(name, profile)
    
    values = {}
    if profile is not None:
        values = profile.data.to_dict()
    
    print(yaml.dump(values))
    
