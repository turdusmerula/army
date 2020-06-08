from army.api.log import log
from army.api.package import Package, PackageException
from army.api.debugtools import print_stack
from army.api.version import Version
import os
import subprocess
import shutil
from schema import Schema, And, Use, Optional

repository_types = {}

def register_repository(repository_class):
    global repository_types
    
    if repository_class.TYPE:
        repository_types[repository_class.TYPE] = repository_class
        log.debug(f"registered '{repository_class.TYPE}' repository type")


# build repository list from configuration
def load_repositories(config, prefix=""):
    global repository_types
    res = []
    
    if prefix=="":
        log.debug(f"load repositories")
    else:
        log.debug(f"load repositories from {prefix}")

    repos = {}
    try:
        repos = config.repo
    except Exception as e:
        print_stack()
        log.debug(f"{e}")
        log.warning("No repository found")
    
    for repo_name in repos:
        try:
            repo_type_name = repos[repo_name].type.value()
            repo_uri = os.path.join(prefix, repos[repo_name].uri.value())

            if repo_type_name in repository_types:
                    
                repo_type = repository_types[repo_type_name]
                
                # instanciate repository and load it
                repo = repo_type(name=repo_name, path=repo_uri)
                res.append(repo)
            else:
                log.warning(f"{repo_type_name}: unhandheld repository type")
        except Exception as e:
            print_stack()
            log.debug(f"{e}")
            log.error(f"{repo_name}: load repository failed")
            
    return res

class RepositoryException(Exception):
    def __init__(self, message):
        self.message = message

# TODO: implement source
class Repository(object):
    TYPE=None
    DEV=False
    
    def __init__(self, name, uri):
        self._name = name
        self._uri = uri
    
    @property
    def uri(self):
        return self._uri
    
    @property
    def name(self):
        return self._name
    
    # override to return package list
    @property
    def packages(self):
        return [] 
    
    @property
    def type(self):
        return self.TYPE
    
    # load package list from repository
    def load(self):
        pass

    # if repository has an internal cache this is where it should be reconstructed
    def update(self):
        self.load()
    
    # search for a package inside the package list
    # @param fullname if True then package name must match exactly, if version is given then fullname is True
    def search(self, name, version=None, fullname=False):
        res = {}
        
        packages = self.packages

        for package in packages:
            match_name = False
            match_version = False
            
            if fullname==False and name in package.description().lower():
                match_name = True
                
            if fullname==True and name==package.name:
                match_name = True
            elif fullname==False and name in package.name:
                match_name = True
            
            if version is None:
                match_version = True
            elif match_name==True and Version(version)==package.version:
                match_version = True
            
            if match_name==True and match_version==True:
                # package match
                max_version = None
                if package.name in res:
                    max_version = res[package.name].version
                
                if max_version is None or package.version>max_version:
                    res[package.name] = package

        return res



class RepositoryPackage(Package):
    def __init__(self, data, path):
        super(RepositoryPackage, self).__init__(data=data, schema={})
        self._path = path
        
    def install(self, path, link):
        includes = self.packaging.include
        includes.append("army.toml")
        
        dest = path

        def rmtree_error(func, path, exc_info):
            print(exc_info)
            exit(1)
        if os.path.exists(path):
            log.debug(f"rm {path}")
            shutil.rmtree(path, onerror=rmtree_error)

        # execute preinstall step
        if os.path.exists(os.path.join(self._path, 'pkg', 'preinstall')):
            subprocess.check_call([os.path.join(self._path, 'pkg', 'preinstall')])

        # check that all files exists
        for include in includes:
            source = os.path.join(self._path, include)
            if os.path.exists(source)==False:
                raise PackageException(f"{include}: package include file not found")

        # create detination tree
        if os.path.exists(dest)==False:
            os.makedirs(dest)
            
        for include in includes:
            source = os.path.join(self._path, include)
            
            if link==True:
                self._link(source, dest)
            else:
                self._copy(source, dest)
        
        # add repository informations to army.toml
        
        #execute postinstall command
        if os.path.exists(os.path.join(self._path, 'pkg', 'postinstall')):
            subprocess.check_call([os.path.join(self._path, 'pkg', 'postinstall')])
        
    def _copy(self, source, dest):
        log.debug(f"copy {source} -> {dest}")
        source = os.path.expanduser(source)
        if os.path.isfile(source):
            shutil.copy(source, os.path.join(dest, os.path.basename(source)))
        else:
            shutil.copytree(source, os.path.join(dest, os.path.basename(source)))

    def _link(self, source, dest):
        log.debug(f"link {source} -> {dest}")
        source = os.path.expanduser(source)
        os.symlink(os.path.abspath(source), os.path.join(dest, os.path.basename(source)))
