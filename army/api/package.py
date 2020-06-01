from army.api.version import Version
from army.api.log import log
import os
import subprocess
import shutil

def find_installed_package(name):
    search_name = name
    search_version = None
    
    if ':' in name:
        search_name, search_version = name.split(':')
    
    
    def _search_dir(path):
        found_package = None
        found_version = None
         
        for package in os.listdir(os.path.expanduser(path)):
            if ':' in package:
                pkg_name, pkg_version = package.split(':')
                if search_version is None:
                    if search_name==pkg_name:
                        if found_version is None:
                            found_version = pkg_version
                            found_package = InstalledPackage(os.path.join(path, package))
                        elif Version(pkg_version)>Version(pkg_version):
                            found_version = pkg_version
                            found_package = InstalledPackage(os.path.join(path, package))
                else:
                    if search_name==pkg_name and Version(search_version)==Version(pkg_version):
                        return InstalledPackage(os.path.join(path, package))
    
        return found_package
    
    # search package in local project
    res = _search_dir('dist')
    if res is not None:
        return res

    # search package in user space 
    res = _search_dir('~/.army/dist')
    return res
    
class PackageException(Exception):
    def __init__(self, message):
        self.message = message

class Package(object):
    def __init__(self, name, description, version, repository):
        self._name = name
        self._description = description
        self._version = Version(version)
        self._repository = repository
        
        self._path = None
        
    def name(self):
        return self._name
    
    def description(self):
        return self._description
    
    def version(self):
        return self._version

    def repository(self):
        return self._repository
    
    def path(self):
        return self._path
    
    # override to provide behavior for loading package data
    def load(self):
        pass
    
    # 
    def dependencies(self):
        return []
    
    def dev_dependencies(self):
        return []

    def plugins(self):
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
        if os.path.exists(os.path.join(self._path, 'pkg', 'preinstall')):
            subprocess.check_call([os.path.join(self._path, 'pkg', 'preinstall')])

        # check that all files exists
        for include in self.include():
            source = os.path.join(self._path, include)
            if os.path.exists(source)==False:
                raise PackageException(f"{include}: package include file not found")

        # create detination tree
        if os.path.exists(dest)==False:
            os.makedirs(dest)
            
        for include in self.include():
            source = os.path.join(self._path, include)
            
            if link==True:
                self._link(source, dest)
            else:
                self._copy(source, dest)
        
        #execute postinstall command
        if os.path.exists(os.path.join(self._path, 'pkg', 'postinstall')):
            subprocess.check_call([os.path.join(self._path, 'pkg', 'postinstall')])
        
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


class InstalledPackage(Package):
    def __init__(self, path):
        # TODO: load package army.toml file and provide informations
#         name = ""
#         description = ""
#         version = ""
#         repository = ""
#         super(InstalledPackage, self).__init__(name, description, version, repository)

        self._path = path
        