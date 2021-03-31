from army.api.log import log
from army.api.package import load_installed_package
from army.api.debugtools import print_stack
from army.api.version import Version
import importlib.util
import os

# cache for loaded plugins
plugins = {}

class PluginException(Exception):
    def __init__(self, message):
        self.message = message

    
def load_plugin(name, version_range, config):
    global plugins
    log.info(f"load plugin '{name}'")
#         
    package = load_installed_package(name, version_range=version_range)
    
    if name in plugins:
        if plugins[name].version==package.version:
            log.info(f"{name}@{plugins[name].version}: plugin already loaded")
        else:
            log.error(f"{name}: trying to load version {package.version} but plugin already loaded with version {plugins[name].version}")
            return 
        
    if package is None:
        log.error(f"{name}: plugin not installed")
        return 

    plugins[name] = package

    try:
        spec = importlib.util.spec_from_file_location("plugin", os.path.join(package.path, '__init__.py'))
        plugin = importlib.util.module_from_spec(spec)
        plugin.config = config
        spec.loader.exec_module(plugin)
    except Exception as e:
        print_stack()
        log.error(e)


class Plugin(object):
    def __init__(self, name, version, config):
        self._name = name
        self._version = version
        self._config = config
    