#!/bin/python3
import shutil
import os
import extargparse
# import commands.build_commands.build
# import commands.build_commands.install
# import commands.build_commands.update
import commands.build_commands.search

def init_parser(parentparser, config):
    group = parentparser.add_parser_group(title='Build commands:')

    # init sub parsers
#     commands.build_commands.build.init_parser(group, config)
#     commands.build_commands.install.init_parser(group, config)
#     commands.build_commands.update.init_parser(group, config)
    commands.build_commands.search.init_parser(group, config)
