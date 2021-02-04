from army.api.log import log
from army.api.package import load_installed_package
from army.api.debugtools import print_stack
from army.api.version import Version
import importlib.util
import os

# cache for loaded plugins
plugins = []

class PluginException(Exception):
    def __init__(self, message):
        self.message = message

    
def load_plugin(name, version_range, config):
    log.info(f"load plugin '{name}'")
#         
    package = load_installed_package(name, version_range=version_range)
 
    if package is None:
        raise PluginException(f"{name}: plugin not installed")
        return

    try:
        spec = importlib.util.spec_from_file_location("plugin", os.path.join(package.path, '__init__.py'))
        plugin = importlib.util.module_from_spec(spec)
        plugin.args = config
        spec.loader.exec_module(plugin)
        plugin.load_plugin()
    except Exception as e:
        print_stack()
        log.debug(e)
        raise PluginException(f"{name}: failed to load plugin")


class Plugin(object):
    def __init__(self, name, version, config):
        self._name = name
        self._version = version
        self._config = config
    