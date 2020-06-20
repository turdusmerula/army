#!/bin/python3
import os
import sys
import pkg_resources
from itertools import chain

sys.path.append(os.path.dirname(pkg_resources.resource_filename(__name__, "army.py")))

from army.api.config import ArmyConfig, load_configuration
from army.api.log import log, get_log_level
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.plugin import load_plugin
from army.api.click import verbose_option 
import army.api.click as click

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

# create the config parser, this parser is mainly used to catch logger verbosity
@click.group(invoke_without_command=True, 
             no_args_is_help=False, 
             add_help_option=False, 
             context_settings=dict(
                 resilient_parsing=True))
@verbose_option()
@click.pass_context
def cli_init(ctx, v, **kwargs):
    # configure logger
    root_config.set("verbose", get_log_level())


# create the top-level parser
@click.group()
@verbose_option()
@click.option('-t', '--target', help='select target')
@click.pass_context
# TODO add version with version_option
def cli(ctx, target, **kwargs):
    global config
    ctx.config = config

    if target is not None:
        config.target = target

@cli.section("Dependencies Management Commands")
@click.pass_context
def dependencies(ctx, **kwargs):
    # recopy parent config in context
    ctx.config = ctx.parent.config

@cli.section("Packaging Commands")
@click.pass_context
def packaging(ctx, **kwargs):
    # recopy parent config in context
    ctx.config = ctx.parent.config

@cli.section("Build Commands", chain=True)
@click.pass_context
def build(ctx, **kwargs):
    # recopy parent config in context
    ctx.config = ctx.parent.config

# path prefix, used to provide unit tests data path
prefix = None
#prefix = os.path.join(os.path.dirname(__file__), "unit_tests/test_project_data")
#prefix = os.path.join(os.path.dirname(__file__), "unit_tests/test_compile_data")
#prefix = os.path.join(os.path.dirname(__file__), "unit_tests/test_data")

def main():
    global prefix
    global config
    
    try:
        # cli_init will initialize the logger only, everything else is ignored at this point
        # we need to load the plugins before showing any help
        cli_init()
    except:
        pass

    # load army configuration files
    if prefix is not None:
        log.debug(f"using {prefix} as path prefix")
    config = load_configuration(parent=root_config, prefix=prefix) 

    # load internal plugins
    import army.plugin.repository
    import army.plugin.dependency
    import army.plugin.package
#     import army.plugin.build

    # load plugins
    # TODO load plugins from installed packages
    if os.path.exists('army.toml'):
        try:
            project = load_project()
            for plugin in project.plugins:
                try:
                    load_plugin(plugin, config)
                except Exception as e:
                    print_stack()
                    print(f"{e}")
        except Exception as e:
            print_stack()
            print(f"army.toml: {e}", file=sys.stderr)
            exit(1)
    # parse command line
    cli() 
    
    
if __name__ == "__main__":

    main()
