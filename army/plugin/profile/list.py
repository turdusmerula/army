from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.log import log
from army.api.path import path
from army.api.profile import load_profile_list, load_profile
from army.api.version import Version
import sys

# TODO: implement profile description
@parser
@group(name="profile")
@command(name="profile")
@command(name='list', help='List available profiles')
@option(name='all', shortcut='a', default=False, help='List all versions', flag=True)
def profile_list(ctx, all, **kwargs):
    log.info(f"profile list")

    profiles = load_profile_list()
    profiles = sorted(profiles, key=_compare_name_version)
    
    if all==False:
        # TODO
        pass
    
    if len(profiles)==0:
        print("no profile found", file=sys.stderr)
        return

    column_name = ['name']
    column_version = ['version']
    column_description = ['description']
    column_path = ['path']

    for profile in profiles:
        try:
            profile.load(validate=False)
            column_name.append(profile.name)
            if profile.version is None:
                column_version.append("")
            else:
                column_version.append(profile.version)
            column_path.append(path(profile.path))
            column_description.append(profile.description)
        except Exception as e:
            print_stack()
            log.error(f"{e}")

    max_name = len(max(column_name, key=len))
    max_version = len(max(column_version, key=len))
    max_path = len(max(column_path, key=len))
    max_description = len(max(column_description, key=len))
  
    for i in range(len(column_name)):
        print(f"{column_name[i].ljust(max_name)} | ", end='')
        print(f"{column_version[i].ljust(max_version)} | ", end='')
        print(f"{column_path[i].ljust(max_path)} | ", end='')
        print(f"{column_description[i].ljust(max_description)} | ", end='')
        print()

def _compare_name_version(profile):
    try:
        return ( profile.name, Version(profile.version) )
    except:
        return ( profile.name, Version("0.0.0") )
        
#     print("---", profile, profile.name, profile.version, type(profile.version))
