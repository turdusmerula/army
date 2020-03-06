#!/bin/python3
import shutil
import os
import extargparse
import commands.project_commands.create

def init_parser(parentparser):
    # create the parser for the "a" command
    group = parentparser.add_parser_group(title='Project commands:')
    parser = group.add_parser('project', help='Manage project')
    subparser = parser.add_subparsers(metavar='COMMAND', title="Commands", description=None, help=None, parser_class=extargparse.ArgumentParser, required=True)

    # init sub parsers
    commands.project_commands.create.init_parser(subparser)
