import toml
import os
import shutil
from log import log
from debugtools import print_stack
from version import Version
from config import load_module

def search_module(module):
    if ':' in module:
        name = module.split(':')[0]
        version = module.split(':')[1]
    else:
        name = module
        version = None
    
    for path in ['dist', '~/.army/dist']:
        for folder in os.listdir(os.path.expanduser(path)):
            if os.path.isdir(os.path.join(path, folder)) and '@' in folder:
                module_name, module_version = folder.split('@')
                
                if module_name==name:
                    if version and Version(version)==Version(module_version):
                        return { 'path': path, 'module': folder}
                    elif version is None:
                        return { 'path': path, 'module': folder}

    return None


def load_dependencies(config, target):
    res = []

    loaded = []
    
    dependencies = config.dependencies()
    
    while(len(dependencies))>0:
        dependency = dependencies.pop()
        if dependency not in loaded:
            module = search_module(dependency)
            if module is None:
                raise DependencyException(f"dependency {dependency} not installed")
            
            # add module properties
            module_config = load_module(None, os.path.join(module['path'], module['module']))
            module['config'] = module_config
            res.append(module)
            
            dependencies += module_config.dependencies()
            
            loaded.append(dependency)

    return res

def load_dev_dependencies(config, target):
    res = []

    loaded = []
    
    dependencies = config.dev_dependencies()
    if len(dependencies)==0:
        dependencies = config.dependencies()
    
    while(len(dependencies))>0:
        dependency = dependencies.pop()
        if dependency not in loaded:
            module = search_module(dependency)
            if module is None:
                raise DependencyException(f"dependency {dependency} not installed")
            
            # add module properties
            module_config = load_module(None, os.path.join(module['path'], module['module']))
            module['config'] = module_config
            res.append(module)
            
            module_dependencies = module_config.dev_dependencies()
            if len(module_dependencies)==0:
                module_dependencies = module_config.dependencies()
            dependencies += module_dependencies
            
            loaded.append(dependency)

    return res

class DependencyException(Exception):
    def __init__(self, message):
        self.message = message
        