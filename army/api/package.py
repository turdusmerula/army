from army.api.version import Version
from army.api.log import log
from army.api.debugtools import print_stack
from army.api.schema import Schema, String, VersionString, Optional, PackageString, Array, Dict, VariableDict, Variant
import os
import toml
import shutil

def load_installed_packages(local=True, _global=True, prefix=""):
    res = []

    def _search_dir(path):
        if os.path.exists(os.path.expanduser(path))==False:
            return []
        
        res = []
        for package in os.listdir(os.path.expanduser(path)):
            try:
                pkg = _load_installed_package(os.path.join(path, package))
                res.append(pkg)
            except Exception as e:
                print_stack()
                log.debug(e)
                log.error(f"{os.path.join(path, package)}: not a valid package")
                
        return res
    
    # search package in local project
    if local:
        res += _search_dir('dist')
    if res is not None:
        return res

    # search package in user space
    if _global: 
        res += _search_dir(os.path.join(prefix, '~/.army/dist'))

    return res

def load_installed_package(name, local=True, _global=True, prefix=""):
    res = None
    
    def _search_dir(path):
        if os.path.exists(os.path.expanduser(path))==False:
            return None

        found_package = None
        found_version = None
         
        for package in os.listdir(os.path.expanduser(path)):
            if name==package:
                return _load_installed_package(os.path.join(path, package))
    
        return found_package
    
    # search package in local project
    if local:
        res = _search_dir('dist')

    # search package in user space
    if res is None and _global: 
        res = _search_dir(os.path.join(prefix, '~/.army/dist'))
    
    return res

def _load_installed_package(path):
    # TODO find a way to add line to error message
    file = os.path.expanduser(os.path.join(path, 'army.toml'))
    if os.path.exists(file)==False:
        raise PackageException(f"{file}: file not found")

    content = {}
    try:
        log.info(f"load installed package '{file}'")
        content = toml.load(file)
        log.debug(f"content: {content}")
    except Exception as e:
        print_stack()
        log.debug(e)
        raise PackageException(f"{format(e)}")
    
    project = InstalledPackage(data=content, path=path)
    project.check()

    return project

    
class PackageException(Exception):
    def __init__(self, message):
        self.message = message

class Package(Schema):
    def __init__(self, data, schema):
        super(Package, self).__init__(data, schema={
                **schema,
                'name': String(),
                'description': String(),
                'version': VersionString(),
                'arch': Optional(String()),
                'dependencies': Optional(VariableDict(PackageString(), VersionString())),
                'plugins': Optional(VariableDict(PackageString(), VersionString())),
                'plugin': Optional(VariableDict(PackageString(), Variant())),
                'packaging': Optional(Dict({
                    'include': Optional(Array(String())),
                    'exclude': Optional(Array(String()))
                    }))
           })
    
    @property
    def name(self):
        return self._data['name']
    
    @property
    def description(self):
        return self._data['description']
    
    @property
    def version(self):
        return Version(self._data['version'])
    # 
    @property
    def arch(self):
        if 'arch' in self._data:
            return self._data['arch']
        return None

    @property
    def dependencies(self):
        if 'dependencies' in self._data:
            return self._data['dependencies']
        return []
    
    @property
    def plugins(self):
        if 'plugins' in self._data:
            return self._data['plugins']
        return []
    
    @property
    def plugin(self):
        if 'plugin' in self._data:
            return self._data['plugin']
        return []

    @property
    def packaging(self):
        class Packaging(object):
            def __init__(self, data):
                self._data = data
        
            @property
            def include(self):
                if 'include' in self._data:
                    return self._data['include']
                return []
        
            @property
            def exclude(self):
                if 'exclude' in self._data:
                    return self._data['exclude']
                return []

        if 'packaging' in self._data:
            return Packaging(self._data['packaging'])
        return Packaging({})

    def __repr__(self):
        return f"{self.name}:{self.version}"

class InstalledPackage(Package):
    def __init__(self, data, path):
        super(InstalledPackage, self).__init__(data, schema={
                'repository': Variant()
            })

        self._path = path
        
    @property
    def path(self):
        return self._path

    @property
    def repository(self):
        class Repository(object):
            def __init__(self, data):
                self._data = data
        
            @property
            def name(self):
                return self._data['name']
        
            @property
            def uri(self):
                return self._data['uri']

        return Repository(self._data['repository'])

    def uninstall(self):
        def rmtree_error(func, path, exc_info):
            print(exc_info)
            exit(1)
        if os.path.exists(self._path):
            log.debug(f"rm {self._path}")
            shutil.rmtree(self._path, onerror=rmtree_error)
    