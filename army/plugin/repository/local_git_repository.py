from army.api.debugtools import print_stack
from army.api.dict_file import load_dict_file
from army.api.log import log
from army.api.package import Package
from army.api.project import load_project, Project
from army.api.repository import Repository, RepositoryPackage
from army.api.version import Version, VersionRange
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
        
    # load package list from repository
    def load(self):
        # load project file
        # TODO find a way to add line to error message

        content = load_dict_file(path=self.uri, name="army")

        self._project = RepositoryPackage(data=content, repository=self)
        self._project.check()
        
    @property
    def packages(self):
        return [self._project] 

    def update(self):
        # nothing to do in a local repository
        pass

    # search for a package inside the package list
    # @param fullname if True then package name must match exactly, if version is given then fullname is True
    def search(self, name, version=None, fullname=False):
        return super(LocalGitRepository, self).search(name, version, fullname)
