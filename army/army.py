#!/bin/python3
import os
import sys
import pkg_resources

sys.path.append(os.path.dirname(pkg_resources.resource_filename(__name__, "army.py")))
import extargparse
import commands.project
import commands.build

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

class Config():
    def __init__(self):
        self.repositories = []
        self.config = {}
        self.plugins = {}
    
    def load_repositories(self):
        pass
    
    def load_config(self):
        pass
    
    def load_plugins(self):
        pass
    
    def load(self):
        pass

def main():
#     parser = extargparse.ArgumentParser(
#         prog="army",
#         description='Arm cross compiling toolset',
#         usage=""" army COMMAND
# 
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

    # create the top-level parser
    parser.add_argument('--foo', action='store_true', help='foo help')
    subparser = parser.add_subparsers(metavar='COMMAND', title=None, description=None, help=None, parser_class=extargparse.ArgumentParser, required=True)

    # load army components parsers
    commands.project.init_parser(subparser)
    commands.build.init_parser(subparser)
    
    # parse command line
    args = parser.parse_args()

    # load army configuration files, each file supesedes the previous
    # Global configuration: /etc/army/army.toml
    # User configuration: ~/.army/army.tom
    # Project configuration: .army/army.toml

    # load repository sources, local repositories are explored first
    # Project sources: .army/sources.toml, .army/sources.d/*.toml
    # User configuration: ~/.army/sources.tom, ~/.army/sources.d/*.toml
    # Global configuration: /etc/army/sources.toml, ~/army/sources.d/*.toml
    
    # load plugins
    # Project plugins:
    # User plugins:
    # Global plugins:

    config = Config()
    config.load()
    
    # call asked command
    args.func(args, config)

if __name__ == "__main__":

    main()
