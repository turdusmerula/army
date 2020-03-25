#!/bin/python3
import os
import sys
import pkg_resources

sys.path.append(os.path.dirname(pkg_resources.resource_filename(__name__, "army.py")))
import extargparse
import argparse
import commands.build
# import commands.project
# import commands.packaging
# import commands.dependencies
from config import load_configuration, load_project
from plugin import load_plugin
from log import log
from debugtools import print_stack

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

parser = extargparse.ArgumentParser(prog='army')


def main():
# Management commands:
#     project    Manage project
#     board      Manage boards
#     
# Remote package commands:
#     search     Search a package on repositories
#     update     Update available package list
#     install    Install package
#     provides   Search for a file inside packages
#     
# Installed package commands:
#     list       List installed packages
#     remove     Uninstall package
#     
# Packaging commands:
#     package    Create package for the current board
#     publish    Publish package on repo
#     tag        Tag version
#     
# Build commands:
#     build      Build project
#     clean      Clean project
#     flash      Flash project on board
#     console    Open console on jtag interface
# """)

    # parse command line for logging arguments
    preparser = extargparse.ArgumentParser(prog='army', add_help=False)
    preparser.add_default_args()
    # check if command has logging arguments, then it can activate debug mode early
    preparser.parse_default_args()
    
    # create the top-level parser
    parser.add_argument('--version', action='store_true', help='return version')
    parser.add_default_args()

    config = load_configuration() 

    # add army default commands
    subparser = parser.add_subparsers(metavar='COMMAND', title=None, description=None, help=None, parser_class=extargparse.ArgumentParser, required=True)

    # load default plugins
    # TODO
#     commands.project.init_parser(subparser, config)
#     commands.packaging.init_parser(subparser, config)
#     commands.dependencies.init_parser(subparser, config)

    # load commands
    commands.build.init_parser(subparser, config)
    
    # load plugins
    try:
        project_config = load_project(config)
        plugins = project_config.plugins()
        for plugin in plugins:
            try:
                load_plugin(plugin, config, subparser)
            except Exception as e:
                print_stack()
                log.warn(f"{e}")
    except Exception as e:
        pass

    # parse command line
    parser.parse_default_args()
    args = parser.parse_args()

    # TODO: version
    
    # load plugins
    # Project plugins:
    # User plugins:
    # Global plugins:

    # call asked command
    args.func(args, config)

if __name__ == "__main__":

    main()
