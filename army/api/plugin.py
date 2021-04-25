from army.api.log import log
from army.api.package import load_installed_package
from army.api.debugtools import print_stack
from army.api.version import Version
import importlib.util
import os
import sys

# cache for loaded plugins
plugins = {}

class PluginException(Exception):
    def __init__(self, message):
        self.message = message

    
def load_plugin(name, version_range, config):
    global plugins
    log.info(f"load plugin '{name}@{version_range}'")
#         
    package = load_installed_package(name, version_range=version_range, exist_ok=True)
    
    if name in plugins:
        if plugins[name].version==package.version:
            log.info(f"{name}@{plugins[name].version}: plugin already loaded")
        else:
            log.error(f"{name}: trying to load version {package.version} but plugin already loaded with version {plugins[name].version}")
            return 
        
    if package is None:
        log.error(f"{name}@{version_range}: plugin not installed")
        return 

    plugins[name] = package

    try:
        for plugin in package.plugins:
            location = os.path.join(package.path, plugin, '__init__.py')
            sys.path.insert(0, os.path.dirname(location))

            spec = importlib.util.spec_from_file_location(name=plugin, location=location)
            module = importlib.util.module_from_spec(spec)
            module.config = config
            spec.loader.exec_module(module)
            
            sys.path.pop(0)
    except Exception as e:
        print_stack()
        log.error(f"loading plugin '{name}' failed: {e}")
        sys.path.pop(0)

    
class Plugin(object):
    def __init__(self, name, version, config):
        self._name = name
        self._version = version
        self._config = config
    