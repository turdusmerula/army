from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.dict_file import Dict
from army.api.log import log
from army.api.plugin import load_plugin
from army.api.profile import load_profile, save_current_profile_cache
import sys

@parser
@group(name="profile")
@command(name="profile")
@command(name='set', help='Set current profile')
@argument(name="profiles", help="[PROFILE] ...", count='*')
def profile_set(ctx, profiles, **kwargs):
    log.info(f"profile set {' '.join(profiles)}")

    profile = None
    
    try:
        for name in profiles:
            profile = load_profile(name, profile)
    except:
        pass

    # load plugins
    plugins = []
    if profile is not None:
        plugins = profile.data.get("/plugins", default=[])
        
        # TODO improve error handling
        for plugin in plugins:
            try:
                data = Dict(plugin)
                name = data.get(f"name")
                version = data.get(f"version", default="latest")
                config = data.get(f"config", default={})
                load_plugin(name, version, config, profile=profile)
            except Exception as e:
                print_stack()
                log.error(f"{e}")
                print(f"Error loading plugin {plugin['name']}@{plugin['version']}", file=sys.stderr)

    for name in profiles:
        profile = load_profile(name, profile)

    save_current_profile_cache(profiles)
