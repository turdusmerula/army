#!/bin/python3
import os
import sys
import pkg_resources
from itertools import chain

sys.path.append(os.path.dirname(pkg_resources.resource_filename(__name__, "__main__.py")))

from army.api.command import get_army_parser, create_parser, ArmyBaseParser
from army.api.config import ArmyConfig, load_global_configuration, load_global_configuration_repositories, load_user_configuration, load_user_configuration_repositories
from army.api.debugtools import print_stack
from army.api.log import log, get_log_level
from army.api.plugin import load_plugin
from army.api.prefix import set_prefix_path
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
root_config = ArmyConfig()
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
        log.debug(f"using {prefix} as path prefix")
        set_prefix_path(prefix)

    # load army configuration files
    try:
        config = load_global_configuration(parent=root_config)
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
#     import army.plugin.package
#     import army.plugin.target
    import army.plugin.profile
# #     import army.plugin.build

    # load profile

    # load project
    try:
        print("----", project_file)
        if project_file is not None:
            project = load_project(path=project_file, exist_ok=False)
        else:
            project = load_project(exist_ok=True)
    except Exception as e:
        print_stack()
        print(f"{e}", file=sys.stderr)
        exit(1)

    army_parser.context.project = project
    
#     # load default target if exists
#     if project is not None:
#         # get target config
#         default_target = None
#         if target_name is None and project.default_target:
#             target_name = project.default_target
#             
#         if target_name is not None:
#             if target_name in project.target:
#                 default_target = project.target[target_name]
#             else:
#                 print(f"{target_name}: target not defined in project", file=sys.stderr)
#                 exit(1)
#             log.info(f"current target: {target_name}")
#     
#     if project is not None:
#         # load plugins at project level
#         for plugin in project.plugins:
#             plugin_config = None
#             
#             # search for plugin configuration in project
#             if plugin in project.plugin:
#                 plugin_config = project.plugin[plugin]
#             
#             # search plugin configuration in target
#             if plugin in default_target.plugin:
#                 plugin_config = default_target.plugin[plugin]
#             
#             try:
#                 load_plugin(plugin, config, plugin_config)
#             except Exception as e:
#                 print_stack()
#                 print(f"{e}")
# 
#     if default_target is not None:
#         # load plugins at target level
#         for plugin in default_target.plugins:
#             plugin_config = None
#             
#             # search plugin configuration in target
#             if plugin in default_target.plugin:
#                 plugin_config = default_target.plugin[plugin]
#             
#             try:
#                 load_plugin(plugin, config, plugin_config)
#             except Exception as e:
#                 print_stack()
#                 print(f"{e}")
# 
    # parse command line
    try:
        army_parser.parse(sys.argv)
    except Exception as e:
        print_stack()
        print(f"{e}", file=sys.stderr)
        exit(1)
    
    exit(0)

