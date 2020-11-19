#!/bin/python3
import os
import sys
import pkg_resources
from itertools import chain

sys.path.append(os.path.dirname(pkg_resources.resource_filename(__name__, "__main__.py")))

from army.api.config import ArmyConfig, load_configuration
from army.api.log import log, get_log_level
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.plugin import load_plugin
from army.api.click import verbose_option 
import army.api.click as click

version = "0.1.1"
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
project = None
default_target = None
target_name = None

# due to resilient_parsing this is needed to ensure we quit after cli_init
premature_exit = False

def show_version():
    print(f"army, version {version}")
    print("Copyright (C) 2016 Free Software Foundation, Inc.")
    print("License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>")
    print("")
    print("This is free software; you are free to change and redistribute it.")
    print("There is NO WARRANTY, to the extent permitted by law.")

# create the config parser, this parser is mainly used to catch logger verbosity
@click.group(invoke_without_command=True, 
             no_args_is_help=False, 
             add_help_option=False, 
             context_settings=dict(
                 resilient_parsing=True))
@verbose_option()
@click.option('-t', '--target', help='select target')
@click.option('--version', help='show army version', is_flag=True)
@click.pass_context
def cli_init(ctx, v, target, version, **kwargs):
    global target_name

    if version:
        global premature_exit
        premature_exit = True
        show_version()
        exit(1)
    
    target_name = target

    # configure logger
    root_config.set("verbose", get_log_level())


# create the top-level parser
@click.group()
@verbose_option()
@click.option('-t', '--target', help='select target')
@click.option('--version', help='show army version', is_flag=True)
@click.pass_context
# TODO add version with version_option
def cli(ctx, target, version, **kwargs):
    global config
    global project
    global target_name
    global default_target
        
    ctx.config = config
    ctx.project = project
    ctx.target = default_target
    ctx.target_name = target_name
    
    if target is not None: 
        if target in project.target:
            ctx.target = project.target[target]
            ctx.target_name = target
        else:
            print(f"{target}: target not defined in project", file=sys.stderr)
            exit(1)
        log.info(f"current target: {target}")

@cli.section("Dependencies Management Commands")
@click.pass_context
def dependencies(ctx, **kwargs):
    # recopy parent config in context
    ctx.config = ctx.parent.config
    ctx.project = ctx.parent.project
    ctx.target = ctx.parent.target
    ctx.target_name = ctx.parent.target_name

@cli.section("Packaging Commands")
@click.pass_context
def packaging(ctx, **kwargs):
    # recopy parent config in context
    ctx.config = ctx.parent.config
    ctx.project = ctx.parent.project
    ctx.target = ctx.parent.target
    ctx.target_name = ctx.parent.target_name

@cli.section("Build Commands", chain=True)
@click.pass_context
def build(ctx, **kwargs):
    # recopy parent config in context
    ctx.config = ctx.parent.config
    ctx.project = ctx.parent.project
    ctx.target = ctx.parent.target
    ctx.target_name = ctx.parent.target_name

# path prefix, used to provide unit tests data path
prefix = None
#prefix = os.path.join(os.path.dirname(__file__), "unit_tests/test_project_data")
#prefix = os.path.join(os.path.dirname(__file__), "unit_tests/test_compile_data")
#prefix = os.path.join(os.path.dirname(__file__), "unit_tests/test_data")

def main():
    global prefix
    global config
    global project
    global default_target
    global target_name
    
    try:
        # cli_init will initialize the logger only, everything else is ignored at this point
        # we need to load the plugins before showing any help
        cli_init()
    except:
        pass
    global premature_exit
    if premature_exit:
        exit(1)

    # load army configuration files
    prefix = os.getenv('ARMY_PREFIX', None)
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
        except Exception as e:
            print_stack()
            print(f"army.toml: {e}", file=sys.stderr)
            exit(1)

    # load default target if exists
    if project is not None:
        # get target config
        default_target = None
        if target_name is None and project.default_target:
            target_name = project.default_target
            
        if target_name is not None:
            if target_name in project.target:
                default_target = project.target[target_name]
            else:
                print(f"{target_name}: target not defined in project", file=sys.stderr)
                exit(1)
            log.info(f"current target: {target_name}")
    
    if project is not None:
        # load plugins at project level
        for plugin in project.plugins:
            plugin_config = None
            
            # search for plugin configuration in project
            if plugin in project.plugin:
                plugin_config = project.plugin[plugin]
            
            # search plugin configuration in target
            if plugin in default_target.plugin:
                plugin_config = default_target.plugin[plugin]
            
            try:
                load_plugin(plugin, config, plugin_config)
            except Exception as e:
                print_stack()
                print(f"{e}")

    if default_target is not None:
        # load plugins at target level
        for plugin in default_target.plugins:
            plugin_config = None
            
            # search plugin configuration in target
            if plugin in default_target.plugin:
                plugin_config = default_target.plugin[plugin]
            
            try:
                load_plugin(plugin, config, plugin_config)
            except Exception as e:
                print_stack()
                print(f"{e}")

    # parse command line
    cli() 
    
