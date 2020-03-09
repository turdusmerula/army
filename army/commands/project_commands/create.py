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
    parser = parentparser.add_parser('create', help='Create a new project')
    parser.add_argument('--type', default='firmware', help='Project type (firmware, library or plugin)')
    parser.add_argument('NAME', help='Project name')
    parser.set_defaults(func=project_create)

def project_create(args, config, **kwargs):
    project_name = args.NAME
    project_type = args.type
    
    if project_type=='firmware':
        template = 'firmware-template'
    elif project_type=='library':
        template = 'library-template'
    elif project_type=='plugin':
        template = 'plugin-template'
    else:
        print(f"army: '{project_type}' is not a valid project type", file=sys.stderr)
        exit(1)
        
    if project_name.isalnum()==False:
        print(f"army: '{project_name}' is not a valid project name", file=sys.stderr)
        exit(1)

    project_path = os.path.join(os.getcwd(), project_name)
    if os.path.exists(project_path):
        print(f"army: '{project_name}' is not empty", file=sys.stderr)
        exit(1)
        
    data_path = Path(os.path.dirname(pkg_resources.resource_filename(__name__, "army.py"))).parent.parent
    shutil.copytree(os.path.join(data_path, template), project_name)

    # replace templates values
    if project_type=='firmware':
        ArmyTemplate(os.path.join(project_path, "firmware.toml")).generate(project_name=project_name)
    elif project_type=='library':
        ArmyTemplate(os.path.join(project_path, "library.toml")).generate(project_name=project_name)
    elif project_type=='plugin':
        ArmyTemplate(os.path.join(project_path, "plugin.toml")).generate(project_name=project_name)

    # files to add to git    
    files = []
    for path in Path(project_path).rglob('*'):
        files.append(os.path.relpath(path, project_path))

    # create git repo
    repo = Repo.init(project_path)

    # first commit
    repo.index.add(files)
    repo.index.commit("initial commit")

    print(f"Project '{project_name}' sucessfully created")
