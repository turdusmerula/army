from army.api.repository import Repository
from army.api.project import load_project
from army.api.debugtools import print_stack
from army.api.log import log
from army.api.package import Package

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
        try:
            project = load_project(prefix=self.uri())
        except Exception as e:
            print_stack()
            log.warning(f"{e}")
            log.warning(f"{self.name()}: loading repository failed")

        self._packages = []
        if project is not None:
            package = Package(
                name=project.project.name.value(), 
                description=project.project.description.value(), 
                version=project.project.version.value())
        
            self._packages.append(package)
            
    def packages(self):
        return self._packages 
