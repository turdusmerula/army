#!/bin/python3
import shutil
import os
import extargparse
import commands.packaging_commands.package

def init_parser(parentparser, config):
    group = parentparser.add_parser_group(title='Packaging commands:')

    # init sub parsers
    commands.packaging_commands.package.init_parser(group, config)
