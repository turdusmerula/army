#!/bin/python3
import shutil
import os
import extargparse
import pkg_resources
import sys
from pathlib import Path
from template import ArmyTemplate
from git import Repo
from config import Config
from package import Package
from config import load_project_configuration

class PackageConfig(Config):
    def __init__(self, parent):
        super(PackageConfig, self).__init__(parent)
    
    def get_includes(self):
        if 'include' in self.config:
            return self.config['include']
        return []
            
def init_parser(parentparser, config):
    # create the parser for the "a" command
    parser = parentparser.add_parser('package', help='Package project')
    parser.add_argument('-o', '--output', default='', help='Output folder')
    parser.set_defaults(func=packaging_package)

def packaging_package(args, config, **kwargs):
    print("[PACKAGE]")

    config = load_project_configuration(config)
    if not config:
        print("army: not a project")

    output_path = args.output

    package_name = config.project_name()+"-"+config.project_version()+".army"
    package = Package()
    package.create_package(config.project_path(), package_name)
    
#     if output_path!='':
#         try:
#             os.makedirs(output_path)
#         except Exception as e:
#             print(format(e))
#             exit(1)
#     
    # TODO implement excludes
    
    # load included folders
    for path in config.includes():
        package.add_files(path)
    package.add_files('army.toml')
    package.package()