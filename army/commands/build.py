#!/bin/python3
import shutil
import os
import extargparse
import commands.build_commands.compile

def init_parser(parentparser, config):
    group = parentparser.add_parser_group(title='Build commands:')

    # init sub parsers
    commands.build_commands.compile.init_parser(group, config)
