#!/bin/python3
import os
import sys
import pkg_resources
from itertools import chain

sys.path.append(os.path.dirname(pkg_resources.resource_filename(__name__, "__main__.py")))

from army.api.command import get_army_parser, create_parser, ArmyBaseParser
from army.api.config import Config, load_global_configuration, load_global_configuration_repositories, load_user_configuration, load_user_configuration_repositories
from army.api.debugtools import print_stack
from army.api.dict_file import Dict
from army.api.log import log, get_log_level
from army.api.path import set_prefix_path
from army.api.plugin import load_plugin
from army.api.profile import load_current_profile, profiles
from army.api.project import load_project

version = "0.1.2"
# TODO add autocomplete https://kislyuk.github.io/argcomplete/

# Git coupling
# see https://git-scm.com/docs/git-worktree

# configuration:
# /etc/army        # global to all users configuration
# ~/.army          # local user configuration
# <project>/.army  # local project configuration

# type of repositories
#  - http: indexed repository with versioned tar files only
#  - remote git: allow to install pushed master/tagged version directly from git
#  - local git: allow to install dev versions with symbolic links 

# /etc/army/
#   repo.d/
#   army.toml

# ~/.army/
#   repo.d/
#   army.toml
 
# <project>/.army/
#   repo.d/
#   army.toml

# firmware project structure:
# board/    # contain supported boards
#   board-1/
#     cmake/
#       board.cmake      # board specific cmake file
#       packages.cmake   # managed by army, references installed packages
#     core/  # contains board specific code
#       board.h
#       init.cpp
#     ld/    # contains ld scripts
#     packages/  # contains army installed packages
#     board.toml  # board description and dependencies
#   board-2/
#   <...>
# firmware/  # firmware, not specific to any board
# output/    # build result
# project.toml # project description and global dependencies

# default configuration
config = None
project_file = None
default_target = None
target_name = None

def option_show_version(ctx, value):
    print(f"army, version {version}")
    print("Copyright (C) 2016 Free Software Foundation, Inc.")
    print("License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>")
    print("")
    print("This is free software; you are free to change and redistribute it.")
    print("There is NO WARRANTY, to the extent permitted by law.")
    exit(0)

def option_project_file(ctx, value):
    global project_file
    project_file = value
    
def main():
    global prefix
    global config
    global project_file
    global default_target
    global target_name
    
    army_parser = get_army_parser()
    army_parser.context.config = config
    army_parser.add_option(name="file", shortcut="f", help="Project file to use", value="FILE", default=None, callback=option_project_file)
    army_parser.add_option(name="version", help="Show version", flag=True, callback=option_show_version)

    sys.stdout = None
    sys.stderr = None
    try:
        # we only want to initialize the logger here, everything else is ignored at this point
        # we need to load the plugins before showing any help
        army_parser.parse(sys.argv[:])
    except Exception:
        pass
    except SystemExit:
        pass
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    
    # set prefix path
    prefix = os.getenv('ARMY_PREFIX', None)
    if prefix is not None:
        log.debug(f"ARMY_PREFIX={prefix}")
        set_prefix_path(prefix)

    # load army configuration files
    try:
        log.debug("load configuration")
        config = load_global_configuration()
        config = load_global_configuration_repositories(parent=config)
        config = load_user_configuration(parent=config)
        config = load_user_configuration_repositories(parent=config)
    except Exception as e:
        print_stack()
        print(f"{e}", file=sys.stderr)
        exit(1)
    
    # set context
    army_parser.context.config = config
    
    # load internal plugins
    import army.plugin.repository
    import army.plugin.dependency
    import army.plugin.package
    import army.plugin.profile
    import army.plugin.project

    # load profile
    profile = None
    try:
        # plugins are not yet loaded so validate of profiles may fail 
        # we will validate the content later after plugins are loaded
        profile = load_current_profile(validate=False)
    except Exception as e:
        print_stack()
        log.error(f"{e}")
        print(f"Error loading profile", file=sys.stderr)
    army_parser.context.profile = profile

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
                load_plugin(name, version, config, profile)
            except Exception as e:
                print_stack()
                log.error(f"{e}")
                print(f"Error loading plugin {plugin['name']}@{plugin['version']}", file=sys.stderr)

    # load project
    project = None
    try:
        if project_file is not None:
            project = load_project(path=project_file, exist_ok=False, profile=profile)
        else:
            project = load_project(exist_ok=True, profile=profile)                
    except Exception as e:
        print_stack()
        log.fatal(f"{e}")        
        print(f"Error loading project", file=sys.stderr)
        exit(1)
    army_parser.context.project = project

    # load profile
    profile = None
    try:
        if profiles is not None:
            for profile in profiles:
                profile.check()
#         profile = load_current_profile()
    except Exception as e:
        print_stack()
        log.error(f"{e}")
        print(f"Error loading profile", file=sys.stderr)

    # parse command line
    try:
        army_parser.log_level = "fatal"
        army_parser.parse(sys.argv)
    except Exception as e:
        print_stack()
        print(f"{e}", file=sys.stderr)
        exit(1)
    
    exit(0)

