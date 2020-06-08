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

def load_local_git_repository(path='army.toml'):
    
    # TODO find a way to add line to error message
    file = os.path.expanduser(path)
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
    
    repo = RepositoryPackage(data=content, path=os.path.dirname(path))
    repo.check()

    return repo

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
        self._project = load_local_git_repository(os.path.join(prefix, self.uri, 'army.toml'))
    
    @property
    def packages(self):
        return [self._project] 

    def update(self):
        # nothing to do in a local repository
        pass
