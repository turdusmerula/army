from army.api.repository import Repository, RepositoryPackage
from army.api.project import load_project, Project
from army.api.debugtools import print_stack
from army.api.log import log
from army.api.package import Package
from army.army import prefix
import os
import toml

class LocalGitRepositoryException(Exception):
    def __init__(self, message):
        self.message = message

class LocalGitRepository(Repository):
    TYPE="git-local"
    DEV=True
    
    def __init__(self, name, path):
        super(LocalGitRepository, self).__init__(name=name, uri=path)

        self._project = None
        
        self.load()
        
    # load package list from repository
    def load(self):
        # load project file
        # TODO find a way to add line to error message
        file = os.path.expanduser(os.path.join(prefix, self.uri, 'army.toml'))
        if os.path.exists(file)==False:
            raise LocalGitRepositoryException(f"{file}: file not found")
    
        content = {}
        try:
            log.info(f"Load git repository '{file}'")
            content = toml.load(file)
            log.debug(f"content: {content}")
        except Exception as e:
            print_stack()
            log.debug(e)
            raise LocalGitRepositoryException(f"{format(e)}")
        
        self._project = RepositoryPackage(data=content, repository=self)
        self._project.check()
        
    @property
    def packages(self):
        return [self._project] 

    def update(self):
        # nothing to do in a local repository
        pass
