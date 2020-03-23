from repository import load_repositories
from config import load_project
from version import Version
from log import log
from debugtools import print_stack
import os

def init_parser(parentparser, config):
    parser = parentparser.add_parser('install', help='Install module')
    parser.add_default_args()
    parser.add_argument('-l', '--link', action='store_true', help='Link files for dev libraries', default=False)
    parser.add_argument('-g', '--global', action='store_true', help='Install library in user space', default=False)
    parser.add_argument('NAME', nargs='*', help='Module names', default=[])
    parser.set_defaults(func=project_install)

def project_install(args, config, **kwargs):
    try:
        # load project configuration
        config = load_project(config)
        if not config:
            print("army: not a project")
    except Exception as e:
        log.error(f"army: {e}")
        print_stack()
        return

    # build repositories list
    repositories = load_repositories(config)
    
    modules = args.NAME
    if len(modules)==0:
        print(config.config)
        
        # find project dependencies
        plugins = config.plugins()
        log.debug(f"plugins: {plugins}")

        dependencies = config.dependencies()
        log.debug(f"dependencies: {dependencies}")
        
        dev_dependencies = config.dev_dependencies()
        log.debug(f"dev-dependencies: {dev_dependencies}")
        
        modules = dependencies+dev_dependencies+plugins
    
    # check install folder
    if getattr(args, 'global'):
        path = "~/.army/dist/"
    else:
        path = "dist"
    
    link = False
    if args.link:
        link = True
        
    for module in modules:
        install_module(module, config, repositories, path, link)
    
def install_module(module, config, repositories, dest_path, link=False):
    print(f"install {module}")

    modules = []
    # search for module in repositories
    for r in repositories:
        repo_config = r['config']
        repo = r['repo']
        modules += repo.search(module, fullname=True)
        
    if len(modules)==0:
        print(f"component not found '{module}'")
        exit(1)
    
    install = None
    for module in modules:
        if module['version']=='dev':
            install = module
        elif install is None:
            install = module
        else:
            if Version(install['version'])>Version(module['version']):
                install = module
            
    # install dependencies
    if 'dependencies' in install['info']:
        for dependency in install['info']['dependencies']:
            install_module(dependency, config, repositories, dest_path, link)
    
    print(f"+++ {install}")
    # check if module already installed
    module_folder = f"{install['name']}@{install['version']}"
    if os.path.exists(os.path.join(module_folder)):
        log.info(f"module '{module_folder}' already installed")
    else:
        pass
    
    try:
        install['repository'].install(install, config, link)
    except Exception as e:
        print(f"army: {e}")
        exit(1)
