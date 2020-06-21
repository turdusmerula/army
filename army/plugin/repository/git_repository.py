from army.api.repository import Repository
from army.api.log import log

class GitRepositoryException(Exception):
    def __init__(self, message):
        self.message = message

class GitRepository(Repository):
    TYPE="git"
    DEV=False
    
    def __init__(self, name, path):
        super(GitRepository, self).__init__(name=name, uri=path)
        
        self._packages = []
        
        self.load()

    # load package list from repository
    def load(self):
        raise GitRepositoryException(f"{self.name}: GitRepository: not yet implemented")

    @property
    def packages(self):
        return self._packages 
