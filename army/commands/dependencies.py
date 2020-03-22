#!/bin/python3
import shutil
import os
import extargparse
import commands.dependencies_commands.install

def init_parser(parentparser, config):
    # create the parser for the "a" command
    group = parentparser.add_parser_group(title='Dependencies management commands:')
    parser = group.add_parser('dependencies', help='Manage dependencies')
    subparser = parser.add_subparsers(metavar='COMMAND', title="Commands", description=None, help=None, parser_class=extargparse.ArgumentParser, required=True)

    # init sub parsers
    commands.dependencies_commands.install.init_parser(subparser, config)
