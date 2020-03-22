#!/bin/python3
import shutil
import os
import extargparse
import pkg_resources
import sys
from pathlib import Path
from template import ArmyTemplate
from git import Repo

def init_parser(parentparser, config):
    # create the parser for the "a" command
    parser = parentparser.add_parser('install', help='Install dependencies')
    parser.add_argument('--type', default='firmware', help='Project type (firmware, library or plugin)')
    parser.set_defaults(func=install_dependencies)

def install_dependencies(args, config, **kwargs):
    pass