from army.api.log import log
from army.api.package import Package
from army.api.debugtools import print_stack

repository_types = {}

def register_repository(repository_class):
    global repository_types
    
    if repository_class.TYPE:
        repository_types[repository_class.TYPE] = repository_class
        log.debug(f"registered '{repository_class.TYPE}' repository type")

# build repository list from configuration
def load_repositories(config):
    global repository_types
    res = []
    
    print(repository_types)
    repos = {}
    try:
        repos = config.repo
    except Exception as e:
        print_stack()
        log.debug(f"{e}")
        log.warning("No repository found")
    
    for repo_name in repos:
        try:
            repo_type = repos[repo_name].type.value()
            
            # instanciate repository and load it
            repo = repository_types[repo_type](repos[repo_name].uri)
            res.append(repo)
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
    
    def __init__(self, uri):
        self._uri = uri
    
    # override to return repository type
    def type(self):
        return None 

    # override if repository has dev capability
    def dev(self):
        return False
    
    # override to return package list
    def packages(self):
        return {} 

    def uri(self):
        return self._uri 


    # load package list from repository
    def load(self):
        pass

    # if repository has an internal cache this is where it should be reconstructed
    def update(self):
        self.load()
    
    # search for a package inside the package list
    # @param fullname if True then package name must match exactly 
    def search(self, package, fullname=False):
        pass


class RepositoryPool(object):
    def __init__(self):
        self._repositories = []
    
    def add_repository(self, repository):
        self._repositories.append(repository)
    
    