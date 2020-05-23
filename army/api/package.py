from army.api.version import Version
from army.api.log import log
import os
import subprocess
import shutil

class PackageException(Exception):
    def __init__(self, message):
        self.message = message

class Package(object):
    def __init__(self, name, description, version, repository):
        self._name = name
        self._description = description
        self._version = Version(version)
        self._repository = repository
        
        self._package_path = None
        
    def name(self):
        return self._name
    
    def description(self):
        return self._description
    
    def version(self):
        return self._version

    def repository(self):
        return self._repository
    
    # override to provide behavior for loading package data
    def load(self):
        pass
    
    # 
    def dependencies(self):
        return []
    
    def dev_dependencies(self):
        return []

    def include(self):
        return []
    
    def exclude(self):
        return []
    
    
    def install(self, path, link):
        print(f"install {self}")
        
        includes = self.include()
        includes.append("army.toml")
        
        dest = path

        # execute preinstall step
        if os.path.exists(os.path.join(self._package_path, 'pkg', 'preinstall')):
            subprocess.check_call([os.path.join(self._package_path, 'pkg', 'preinstall')])

        # check that all files exists
        for include in self.include():
            source = os.path.join(self._package_path, include)
            if os.path.exists(source)==False:
                raise PackageException(f"{include}: package include file not found")

        # create detination tree
        if os.path.exists(dest)==False:
            os.makedirs(dest)
            
        for include in self.include():
            source = os.path.join(self._package_path, include)
            
            if link==True:
                self._link(source, dest)
            else:
                self._copy(source, dest)
        
        #execute postinstall command
        if os.path.exists(os.path.join(self._package_path, 'pkg', 'postinstall')):
            subprocess.check_call([os.path.join(self._package_path, 'pkg', 'postinstall')])
        
    def _copy(self, source, dest):
        log.debug(f"copy {source} -> {dest}")
        source = os.path.expanduser(source)
        if os.path.isfile(source):
            shutil.copy(source, os.path.join(dest, os.path.basename(source)))
        else:
            shutil.copytree(source, os.path.join(dest, os.path.basename(source)))

    def _link(self, source, dest):
        log.debug(f"link {source} -> {dest}")
        source = os.path.expanduser(source)
        os.symlink(os.path.abspath(source), os.path.join(dest, os.path.basename(source)))
        
    def __repr__(self):
        return f"{self._name}:{self._version}"
