from repository import load_repositories
from config import load_project
from version import Version
from log import log
from debugtools import print_stack

# TODO: implement semantic https://semver.npmjs.com/
# check https://www.grzegorowski.com/what-are-npm-dist-tags-how-to-use-them

def init_parser(parentparser, config):
    parser = parentparser.add_parser('search', help='Search module')
    parser.add_default_args()
    parser.add_argument('NAME', help='Module name')
    parser.set_defaults(func=project_search)

def project_search(args, config, **kwargs):
    try:
        # load project configuration
        config = load_project(config)
        if not config:
            print("army: not a project")
    except Exception as e:
        log.error(f"army: {e}")
        print_stack()
        return
        
    name = args.NAME
        
    # build repositories list
    repositories = load_repositories(config)
    
    res = {}
    
    for r in repositories:
        repo_config = r['config']
        repo = r['repo']
        modules = repo.search(name, [])
        if len(modules)>0:
            res[repo] = modules
             
    if len(res)==0:
        print(f'No matches found for "{name}"')

    column_repo = ['repository']
    column_module = ['module']
    column_version = ['version']
    column_description = ['description']
    
    for r in res:
        repo = res[r]
        for module in repo:

            column_repo.append(r.name)
            column_module.append(module['name'])
            column_version.append(module['version'])
            column_description.append(module['info']['description'])

    max_repo = len(max(column_repo, key=len))
    max_module = len(max(column_module, key=len))
    max_version = len(max(column_version, key=len))

    for i in range(len(column_repo)):
        print(f"{column_repo[i].ljust(max_repo, ' ')}|{column_module[i].ljust(max_module)}|{column_version[i].ljust(max_version)}|{column_description[i]}")
    