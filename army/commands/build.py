#!/bin/python3
import shutil
import os
import extargparse
import commands.build_commands.build

def init_parser(parentparser):
    group = parentparser.add_parser_group(title='Build commands:')

    # init sub parsers
    commands.build_commands.build.init_parser(group)
