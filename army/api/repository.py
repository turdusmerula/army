from army.api.log import log
from army.api.package import Package
from army.api.debugtools import print_stack
from army.api.version import Version
import os

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
            log.warning(f"{repo_name}: load repository failed")
            
    return res

class RepositoryException(Exception):
    def __init__(self, message):
        self.message = message


class Repository(object):
    TYPE=None
    DEV=False
    
    def __init__(self, name, uri):
        self._name = name
        self._uri = uri
    
    def uri(self):
        return self._uri
    
    def name(self):
        return self._name
    
    # override to return package list
    def packages(self):
        return [] 


    # load package list from repository
    def load(self):
        pass

    # if repository has an internal cache this is where it should be reconstructed
    def update(self):
        self.load()
    
    # search for a package inside the package list
    # @param fullname if True then package name must match exactly, if version is given then fullname is True
    def search(self, search_criteria, fullname=False):
        res = {}
        
        search_name = search_criteria
        search_version = None
        
        if ':' in search_criteria:
            search_name, search_version = search_criteria.split(':')
            fullname = True
        
        packages = self.packages()
        for package in packages:
            match_name = False
            match_version = False
            
            if fullname==True and search_name==package.name():
                match_name = True
            elif fullname==False and search_name in package.name():
                match_name = True
            
            if search_version is None:
                match_version = True
            elif match_name==True and Version(search_version)==package.version():
                match_version = True
            
            if match_name==True and match_version==True:
                # package match
                max_version = None
                if package.name() in res:
                    max_version = res[package.name()].version()
                
                if max_version is None or package.version()>max_version:
                    res[package.name()] = package

        return res

    
class RepositoryPool(object):
    def __init__(self):
        self._repositories = []
    
    def add_repository(self, repository):
        self._repositories.append(repository)
    
    