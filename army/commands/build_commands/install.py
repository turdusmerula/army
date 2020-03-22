from repository import load_repositories
from config import load_project_configuration

def init_parser(parentparser, config):
    parser = parentparser.add_parser('install', help='Install module')
    parser.add_argument('-l', '--link', action='store_true', help='Link files for dev libraries')
    parser.set_defaults(func=project_install)

def project_install(args, config, **kwargs):
    print("[INSTALL]")
    # load project configuration
    config = load_project_configuration(config)
    if not config:
        print("army: not a project")

    # TODO load repository indexes
    repositories = load_repositories(config)
    
    # TODO search for package in list
    
    # TODO install dependecies
    
    # TODO install dev-dependecies

    # TODO install plugins
    
    pass