import toml
import os
import sys
import shutil
import glob
import tempfile
import zipfile
import urllib
from log import log
from debugtools import print_stack
from version import Version

# type of repositories
#  - http: indexed repository with versioned army packages
#  - local repository: indexed repository with versioned army packages
#  - remote git: allow to install pushed master/tagged version directly from git
#  - local git: allow to install dev versions with symbolic links 


# repository cache is stored in ~/.toml/cache
def load_repository_cache(config):
    res = []
    
    # load user cache
    cache_path = os.path.join(os.path.expanduser('~'), '.army/cache')    
    if os.path.exists(cache_path)==False:
        os.makedirs(cache_path)
    r = RepositoryCache(cache_path)
    r.load()
    res.append(r)
    
#     # load project cache
#     cache_path = '.army/cache'
#     if os.path.exists(cache_path)==True:
#         r = RepositoryCache(cache_path)
#         r.load()
#         res.append(r)
    
    return res

# load repository sources, local repositories are explored first
# Project sources: .army/sources.toml, .army/sources.d/*.toml
# User configuration: ~/.army/sources.tom, ~/.army/sources.d/*.toml
# Global configuration: /etc/army/sources.toml, ~/army/sources.d/*.toml
def load_repositories(config):
    res = []
    
    while config.parent:
        if 'repo' in config.config:
            for irepo in config.config['repo']:
                repo = config.config['repo'][irepo]
                r = Repository(irepo, repo['uri'])
                r.load()
                res.append({ 'config': config, 'repo': r})
        config = config.parent
    return res


class RepositoryException(Exception):
    def __init__(self, message):
        self.message = message
        

class RepositoryCache():
    def __init__(self, path):
        self.path = path
        self.index = {}

    def load(self):
        index_path = os.path.join(self.path, 'index.toml')
        if os.path.exists(index_path):
            self.index = toml.load(index_path)
            log.debug(f"loaded index '{index_path}'")
    
    def add_repository(self, repo):
        self.index[repo.name] = {
            'uri': repo.uri,
            'type': repo.type, 
            'modules': repo.modules
        }
    
    def save(self):
        if len(self.index)>0:
            if os.path.exists(self.path)==False:
                os.makedirs(self.path)
            with open(os.path.join(self.path, 'index.toml'), "w") as f:
                toml.dump(self.index, f)


class Repository():
    def __init__(self, name, uri):
        self.name = name
        self.uri = uri
        self.loaded = False
        self.type = None
        self.modules = {}
        
        self.packages = {}
    
    def loaded(self):
        return self.loaded 
    
    def load(self):
        try:
            uri = os.path.expanduser(self.uri)
            if os.path.exists(uri)==False:
                raise RepositoryException(f"repository '{self.name}' does not exist")
            
            if os.path.exists(os.path.join(uri, 'army.toml')):
                # found a dev repository
                self.type = 'dev'
                project = toml.load(os.path.join(os.path.join(uri, 'army.toml')))
                self.modules = {}
                self.modules[project['project']['name']] = {
                    'dev': {
                        'type': project['project']['type'],
                        'description': project['project']['description']
                    }
                }
                log.info(f"Loaded repository: local dev '{self.uri}'")
    
            elif os.path.exists(os.path.join(uri, 'index.toml')):
                # found a versioned repository
                self.type = 'versioned'
                self.modules = toml.load(os.path.join(os.path.join(uri, 'index.toml')))
                log.info(f"Loaded repository: local versioned '{self.uri}'")
                
                # TODO check file
            else:
                raise RepositoryException(f"repository '{self.uri}' is not valid")
        except Exception as e:
            log.error(f"army: {e}")
            print_stack()
            return
        
        # TODO: add check repository consistency
        self.loaded = True

    def search(self, name, criterias):
        log.info(f"search '{name}' in '{self.uri}'")

        found = []
        for module in self.modules:
            if name in module:
                found.append({'name': module, 'version': self.modules[module]})
        
        res = []
        for module in found:
            # search for greater version
            # TODO search for greater version respecting criterias
            max_version = None
            max_info = None
            for v in module['version']:
                info = module['version'][v]
                if v=='dev':
                    res.append({'name': module['name'], 'version': v, 'info': info})
                elif max_version is None:
                    max_version = v
                    max_info = info
                elif Version(v)>Version(max_version):
                    max_version = v
                    max_info = info
            
            # build result
            if max_version:
                res.append({'name': module['name'], 'version': max_version, 'info': max_info})
        
        log.debug(res)
        return res