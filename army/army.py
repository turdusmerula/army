#!/bin/python3
import os
import sys
import pkg_resources

sys.path.append(os.path.dirname(pkg_resources.resource_filename(__name__, "army.py")))
import extargparse
import argparse

from army.api.config import ArmyConfig, load_configuration
from army.api.log import log, get_log_level
from army.api.debugtools import print_stack
from army.api.command import Command, CommandGroup

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

# library project structure:

# create the top-level parser
# this parser handles top level 
root_parser = extargparse.ArgumentParser(prog='army')
root_config = ArmyConfig()

def main():

    # temporary parser used parse command line for logging arguments, other arguments are ignored during this phase
    # if logging arguments are present they can be activated prior to any action
    preparser = extargparse.ArgumentParser(prog='army', add_help=False)
    preparser.add_default_args()
    preparser.parse_default_args()
    
    # configure logger
    root_config.set("verbose", get_log_level())
    
    # load army configuration files
    config = load_configuration() 

    # add root_parser options
    root_parser.add_argument('--version', action='store_true', help='return version')
    root_parser.add_argument('-t', '--target', help='select target', default=None)
    root_parser.add_default_args()

    # init command parser group
    command_parser = root_parser.add_subparsers(metavar='COMMAND', title=None, description=None, help=None, parser_class=extargparse.ArgumentParser, required=True)
    CommandGroup.init_root("aaa", "aaa", command_parser)
    root = CommandGroup.root()

#     # create default subgroups
#     root.add_subgroup(CommandGroup("package", "Package commands"))
#     root.add_subgroup(CommandGroup("build", "Build commands"))
    
    # load internal plugins
    import army.plugin.package
    
#     # load plugins
#     try:
#         project_config = load_project(config)
#         plugins = project_config.plugins()
#         for plugin in plugins:
#             try:
#                 load_plugin(plugin, config, subparser)
#             except Exception as e:
#                 print_stack()
#                 log.warn(f"{e}")
#     except Exception as e:
#         pass
# 
    # parse command line
    root_parser.parse_default_args()
    args = root_parser.parse_args()

#     # TODO: version
     
    if args.target is not None:
        config.config['command_target'] = args.target
 
    # call asked commands
    while args is not None:
        if hasattr(args, "func"):
            args.func(args, config)
        if hasattr(args, "subspace"):
            args = args.subspace
        else:
            args = None
        
    
if __name__ == "__main__":

    main()
