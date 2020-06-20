from army.api.repository import Repository
from army.api.log import log

class GitlabRepositoryException(Exception):
    def __init__(self, message):
        self.message = message

class GitlabRepository(Repository):
    TYPE="gitlab"
    DEV=False
    
    def __init__(self, name, path):
        super(GitlabRepository, self).__init__(name=name, uri=path)
        
        self._packages = []
        
        self.load()

    # load package list from repository
    def load(self):
        raise GitlabRepositoryException(f"{self.name}: GitlabRepository: not yet implemented")

    def update(self):
        pass
    
    def packages(self):
        return self._packages 
