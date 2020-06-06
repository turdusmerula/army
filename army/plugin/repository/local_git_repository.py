from army.api.repository import Repository
from army.api.project import load_project
from army.api.debugtools import print_stack
from army.api.log import log
from army.api.package import Package
from army.api.project import ArmyProjectFile
from army.army import prefix
import os

class LocalGitPackageException(Exception):
    def __init__(self, message):
        self.message = message

class LocalGitPackage(Package):
    def __init__(self, name, description, version, repository):
        super(LocalGitPackage, self).__init__(
            name=name, 
            description=description, 
            version=version, 
            repository=repository
        )

        self._config = None
        
    def load(self):
        try:
            self._config = ArmyProjectFile(file=os.path.join(self._repository.uri(), 'army.toml'))
            self._path = self.repository().uri()
        except Exception as e:
            print_stack()
            log.error(e)
            raise LocalGitPackageException(f"{self.name()}: package load failed")
        
    def dependencies(self):
        res = []
        for dependency in self._config.project.dependencies:
            res.append(dependency.value())
        return res
    
    def dev_dependencies(self):
        res = []
        for dependency in self._config.project.get("dev-dependencies"):
            res.append(dependency.value())
        return res

    def plugins(self):
        res = []
        for dependency in self._config.plugin:
            res.append(dependency)
        return res

    def include(self):
        return self._config.packaging.include.value()
    
    def exclude(self):
        return self._config.packaging.exclude.value()

class LocalGitRepository(Repository):
    TYPE="git-local"
    DEV=True
    
    def __init__(self, name, path):
        super(LocalGitRepository, self).__init__(name=name, uri=path)

        self._packages = []
        
        self.load()
        
    # load package list from repository
    def load(self):
        # load project file
        project = None
        project = load_project(prefix=self.uri())

        self._packages = []
        if project is not None:
            package = LocalGitPackage(
                name=project.project.name.value(), 
                description=project.project.description.value(), 
                version=project.project.version.value(),
                repository=self
                )
        
            self._packages.append(package)
            
    def packages(self):
        return self._packages 

    def update(self):
        # nothing to do in a local repository
        pass
