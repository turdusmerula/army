from army.api.repository import Repository
from army.api.log import log

class GitRepository(Repository):
    TYPE="git"
    DEV=False
    
    def __init__(self, name, path):
        super(GitRepository, self).__init__(name=name, uri=path)
        
        self._packages = []
        
        self.load()

    # load package list from repository
    def load(self):
        log.warning(f"{self.name()}: GitRepository.load: not yet implemented")

    def packages(self):
        return self._packages 
