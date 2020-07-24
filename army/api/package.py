from army.api.version import Version, VersionRange
from army.api.log import log
from army.api.debugtools import print_stack
from army.api.schema import Schema, String, VersionString, Optional, PackageString, Array, Dict, VariableDict, Variant, VersionRangeString
import os
import toml
import shutil

def load_installed_packages(local=True, _global=True, prefix=None):
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
        res += _search_dir(os.path.join(prefix or "", '~/.army/dist'))

    return res

def load_installed_package(name, local=True, _global=True, version_range=None, prefix=None):
    res = None
    
    def _search_dir(path, version_range):
        if os.path.exists(os.path.expanduser(path))==False:
            return None
         
        for package in os.listdir(os.path.expanduser(path)):
            if name==package:
                try:
                    pkg = _load_installed_package(os.path.join(path, package))
                    if version_range is None:
                        return pkg
                    else:
                        version_range = VersionRange(version_range, [pkg.version])
                        if version_range.match(Version(pkg.version)):
                            return pkg
                except Exception as e:
                    print_stack()
                    log.debug(e)
                    log.error(f"{os.path.join(path, package)}: not a valid package")
                
        return None
    
    # search package in local project
    if local:
        res = _search_dir('dist', version_range)

    # search package in user space
    if res is None and _global: 
        res = _search_dir(os.path.join(prefix or "", '~/.army/dist'), version_range)
    
    return res

# TODO check version when loading package and in case of package installed both global and local use the best fit
def load_project_packages(project, target):
    loaded = []
    to_load = []
    for dependency in project.dependencies:
        to_load.append((dependency, project.dependencies[dependency]))

    for dependency in project.target[target].dependencies:
        to_load.append((dependency, project.target[target].dependencies[dependency]))

    dependencies = []
    while len(to_load)>0:
        dependency, version_range = to_load.pop(0)
        if dependency not in loaded:
            installed = load_installed_package(dependency, version_range=version_range)
            if installed is None:
                raise PackageException(f"{dependency}: package not installed")
            dependencies.append(installed)
        
            for subdependency in installed.dependencies:
                to_load.append((subdependency, installed.dependencies[subdependency]))
                
            loaded.append(dependency)
        else:
            log.info(f"{dependency} already loaded, skip")
    return dependencies

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
                'dependencies': Optional(VariableDict(PackageString(), VersionRangeString())),
                'plugins': Optional(VariableDict(PackageString(), VersionRangeString())),
                'plugin': Optional(VariableDict(PackageString(), Variant())),
                'packaging': Optional(Dict({
                    'include': Optional(Array(String())),
                    'exclude': Optional(Array(String()))
                    })),
                
                # arch definition
                'arch': Optional(VariableDict(String(), Dict({
                    'definition': Optional(String()),
                    'cpu': Optional(String()),                    
                    }))),

                # in case of a firmware
                'default-target': Optional(String()),
                'target': Optional(VariableDict(String(), Dict({
                    'arch': String(),
                    'definition': Optional(String()),
                    'dependencies': Optional(VariableDict(PackageString(), VersionRangeString())),
                    'plugins': Optional(VariableDict(PackageString(), VersionRangeString())),
                    'plugin': Optional(VariableDict(PackageString(), Variant())),
                    }))),
                
                # in case of a library
                'cmake': Optional(Dict({
                    'include': Optional(String()),
                    })),

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
        class ArchDictIterator(object):
            def __init__(self, values):
                self._list = values
                self._iter = iter(self._list)
             
            def __next__(self):
                return next(self._iter)

        class ArchDict(object):
            def __init__(self, data):
                self._data = data
                
            def __iter__(self):
                return ArchDictIterator(self._data)
            
            def __getitem__(self, item):
                return Arch(self._data[item])
            
        class Arch(object):
            def __init__(self, data):
                self._data = data
            
            @property
            def definition(self):
                if 'definition' in self._data:
                    return self._data['definition']
                return None
            
            @property
            def cpu(self):
                if 'cpu' in self._data:
                    return self._data['cpu']
                return None
            
        if 'arch' in self._data:
            return ArchDict(self._data['arch'])
        return ArchDict({})

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
        
    @property
    def default_target(self):
        if 'default-target' in self._data:
            return self._data['default-target']
        return None
        
    @property
    def target(self):
        class TargetDictIterator(object):
            def __init__(self, values):
                self._list = values
                self._iter = iter(self._list)
             
            def __next__(self):
                return next(self._iter)

        class TargetDict(object):
            def __init__(self, data):
                self._data = data
                
            def __iter__(self):
                return TargetDictIterator(self._data)
            
            def __getitem__(self, item):
                return Target(self._data[item])
            
        class Target(object):
            def __init__(self, data):
                self._data = data
            
            @property
            def arch(self):
                return self._data['arch']
            
            @property
            def definition(self):
                if 'definition' in self._data:
                    return self._data['definition']
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

        if 'target' in self._data:
            return TargetDict(self._data['target'])
        return TargetDict({})

    @property
    def cmake(self):
        class CMake(object):
            def __init__(self, data):
                self._data = data
            
            @property
            def include(self):
                if 'include' in self._data:
                    return self._data['include']
                return None
        if 'cmake' in self._data:
            return CMake(self._data['cmake'])
        return CMake({})
    
    def package(self, output_path):
        """ Packaging command, to be overloaded by package behavior
        """
        pass
    
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
    