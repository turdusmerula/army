#!/bin/python3
import shutil
import os
import extargparse
import pkg_resources
import sys
from pathlib import Path
from template import ArmyTemplate
from git import Repo

def init_parser(parentparser):
#     parser = group.add_parser('build', help='Build commands')
    parser = parentparser.add_parser('build', help='Build project')
    parser.add_argument('--debug', action='store_true', help='turn on debug mode')
    parser.set_defaults(func=project_build)

def project_build(args, config, **kwargs):
    # check if project contains a configuration file
    print(args)