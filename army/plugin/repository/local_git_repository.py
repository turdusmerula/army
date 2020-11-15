from army.api.repository import Repository, RepositoryPackage
from army.api.project import load_project, Project
from army.api.debugtools import print_stack
from army.api.version import Version, VersionRange
from army.api.log import log
from army.api.package import Package
from army import prefix
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
        file = os.path.expanduser(os.path.join(prefix or "", self.uri, 'army.toml'))
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

    # search for a package inside the package list
    # @param fullname if True then package name must match exactly, if version is given then fullname is True
    def search(self, name, version=None, fullname=False):
        versions = {}
        
        packages = self.packages
        
        if version is not None:
            fullname = True
        
        name = name.lower()
        # select packages matching name criteria in package list
        for package in packages:
            match_name = False
            
            if fullname==False and name in package.description.lower():
                match_name = True
                
            if fullname==True and name==package.name:
                match_name = True
            elif fullname==False and name in package.name:
                match_name = True
            
            if match_name==True:
                if package.name in versions:
                    versions[package.name].version.add_version(package.version)
                else:
                    if version is None:
                        # no version specified, give latest by default
                        versions[package.name] = VersionRange('latest', versions=[package.version])
                    else:
                        versions[package.name] = VersionRange(version, versions=[package.version])

        res = {}
        # select packages matching version in found packages
        for name in versions:
            for package in packages:
                if package.version in versions[name]:
                    res[name] = package
                    
        return res
