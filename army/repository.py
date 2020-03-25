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
from config import load_module

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
                log.warning(f"repository '{self.name}' does not exist")
                return 
            
            if os.path.exists(os.path.join(uri, 'army.toml')):
                # found a dev repository
                self.type = 'dev'
                project = toml.load(os.path.join(os.path.join(uri, 'army.toml')))
                self.modules = {}
                module = {
                    'dev': {
                        'type': project['project']['type'],
                        'description': project['project']['description']
                    }
                }
                if 'dependencies' in project['project']:
                    module['dev']['dependencies'] = project['project']['dependencies']
                if 'dev-dependencies' in project['project']:
                    module['dev']['dev-dependencies'] = project['project']['dev-dependencies']
                if 'arch' in project['project']:
                    module['dev']['arch'] = project['project']['arch']
                    
                self.modules[project['project']['name']] = module
                log.info(f"Loaded repository: local dev '{self.uri}'")
    
            elif os.path.exists(os.path.join(uri, 'index.toml')):
                # found a versioned repository
                self.type = 'versioned'
                self.modules = toml.load(os.path.join(os.path.join(uri, 'index.toml')))
                log.info(f"Loaded repository: local versioned '{self.uri}'")
                
                # TODO check file
                log.error("Not implemented yet")
                print_stack()
                exit(1)
            else:
                raise RepositoryException(f"repository '{self.uri}' is not valid")
        except Exception as e:
            log.error(f"army: {e}")
            print_stack()
            return
        
        # TODO: add check repository consistency
        self.loaded = True

    def search(self, module, fullname=False):
        log.info(f"search '{module}' in repo '{self.name}' at '{self.uri}'")

        if ':' in module:
            name = module.split(':')[0]
            version = module.split(':')[1]
            fullname=True
        else:
            name = module
            version = None

        found = []
        for module in self.modules:
            if fullname==False and name in module:
                found.append({'name': module, 'version': self.modules[module]})
            elif fullname==True and name==module:
                found.append({'name': module, 'version': self.modules[module]})

        res = []
        for module in found:
            # search for greater version
            # TODO search for greater version respecting criterias
            max_version = None
            max_info = None
            for v in module['version']:
                info = module['version'][v]

                match = True
                if version:
                    if Version(version)!=Version(v):
                        match = False
                
                if match:
                    if v=='dev':
                        res.append({'repository': self, 'name': module['name'], 'version': v, 'info': info})
                    elif max_version is None:
                        max_version = v
                        max_info = info
                    elif Version(v)>Version(max_version):
                        max_version = v
                        max_info = info
            
            # build result
            if max_version:
                res.append({'repository': self, 'name': module['name'], 'version': max_version, 'info': max_info})
        
        log.debug(res)
        return res

    def build(self, module, config):
        if self.type!='dev':
            # ignore this step
            return
        
        log.info(f"build module '{module['name']}'")
        
        try:
            cwd = os.getcwd()
            os.chdir(os.path.expanduser(self.uri))
        
            # execute prebuild step
            if os.path.exists(os.path.join('pkg', 'prebuild')):
                os.system(os.path.join('pkg', 'prebuild'))
            
            #execute postbuild command
            if os.path.exists(os.path.join('pkg', 'postbuild')):
                os.system(os.path.join('pkg', 'postbuild'))
            
            os.chdir(cwd)
        except Exception as e:
            os.chdir(cwd)
            print_stack()
            log.error(f"{e}")
            raise RepositoryException("Build failed for '{module['name']}' from '{self.name}'")

    def package(self, module, config):
        pass
    
    def install(self, module, config, link=False, force=False):
        module_source = None
        install_name = f"{module['name']}@{module['version']}"
        install_path = 'dist'
        
        log.info(f"install module '{install_name}'")
        
        # check if component exists
        try:
            if os.path.exists(os.path.join(install_path, install_name)):
                if force:
                    # remove component prior to reinstall
                    log.info(f"remove module '{install_name}'")
                    shutil.rmtree(os.path.join(install_path, install_name))
                else:
                    log.info(f"module '{install_name}' already installed")
                    return
        except Exception as e:
            print_stack()
            log.error(f"{e}")
            raise RepositoryException("Install failed for '{module['name']}' from '{self.name}'")
        
        if self.type=='dev':
            module_path = os.path.expanduser(self.uri)
            module_source = module_path
            # build the package prior to install it
            self.build(module, config)
        else:
            link = False
            module_path = os.path.join(self.uri, module['info']['path'])
            
            # check if module exist in repo
            if os.path.exists(module_path):
                raise RepositoryException(f"Component '{module['name']}' missing in repository '{self.name}'")
            # TODO
            # uncompress module
            log.error("Not implemented yet")
            print_stack()
            exit(1)
            
        if module_source is None:
            raise RepositoryException(f"Install failed for '{module['name']}' from '{self.name}'")
        
        # read component 
        config = load_module(config, module_source)
        
        # get files to install
        includes = config.includes()
        if os.path.exists(os.path.join(module_path, 'pkg')):
            includes.append('pkg')
        includes.append('army.toml')
        
        try:
            dest_path = os.path.join(install_path, install_name)
            if os.path.exists(dest_path)==False:
                os.makedirs(dest_path)
            
            # execute preinstall step
            if os.path.exists(os.path.join(module_path, 'pkg', 'preinstall')):
                os.system(os.path.join(module_path, 'pkg', 'preinstall'))
            
            for include in includes:
                if link:
                    os.symlink(os.path.join(module_path, include), os.path.join(dest_path, include))
                else:
                    if os.path.isfile(os.path.join(module_path, include)):
                        shutil.copy(os.path.join(module_path, include), os.path.join(dest_path, include))
                    else:
                        shutil.copytree(os.path.join(module_path, include), os.path.join(dest_path, include))

            #execute postinstall command
            if os.path.exists(os.path.join(dest_path, 'pkg', 'postinstall')):
                os.system(os.path.join(dest_path, 'pkg', 'postinstall'))

            if os.path.exists(os.path.join(dest_path, 'pkg')):
                if link:
                    os.remove(os.path.join(dest_path, 'pkg'))
                else:
                    shutil.rmtree(os.path.join(dest_path, 'pkg'))
            
        except Exception as e:
            print_stack()
            log.error(f"{e}")
            raise RepositoryException(f"Install failed for '{module['name']}' from '{self.name}'")
