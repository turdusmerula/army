from repository import load_repositories, RepositoryCache
from config import load_project_configuration, ProjectConfig
import os

def init_parser(parentparser, config):
    parser = parentparser.add_parser('update', help='Update repository indexes')
    parser.set_defaults(func=project_update)

def project_update(args, config, **kwargs):
    # load project configuration
    config = load_project_configuration(config)
    if not config:
        print("army: not a project")

    # build repositories list
    repositories = load_repositories(config)
    
    # update repositories
    for repo in repositories:
        repo['repo'].update()

    # update caches
    user_cache = RepositoryCache(os.path.join(os.path.expanduser('~'), '.army/cache'))
    project_cache = RepositoryCache('.army/cache')
    for repo in repositories:
        if type(repo['config'])==ProjectConfig:
            project_cache.add_repository(repo['repo']) 
        else:
            user_cache.add_repository(repo['repo']) 
    
    user_cache.save()
    project_cache.save()
