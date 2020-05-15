from army.api.package import Package

class RepositoryException(Exception):
    def __init__(self, message):
        self.message = message


class Repository(object):
    def __init__(self, type, uri):
        self._type = type
        self._uri = uri
        self._packages = {}
    
    def type(self):
        return self._type 

    def uri(self):
        return self._uri 

    def packages(self):
        return self._packages 

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
    
    