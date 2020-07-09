from army.api.log import log
from army.api.package import load_installed_package
from army.api.debugtools import print_stack
from army.api.version import Version
import importlib.util
import os

def load_plugin(name, config, plugin_config):
    log.info(f"load plugin '{name}'")

    search_name = name
    search_version = None
    if ':' in name:
        search_name, search_version = name.split(':')

    if search_name.endswith("-plugin")==False:
        search_name = f"{search_name}-plugin"
        
    package = load_installed_package(search_name)

    if package is None:
        raise PluginException(f"{name}: plugin not installed")
        return

    if search_version and package.version!=Version(search_version):
        raise PluginException(f"{name}: require version '{search_version}' but '{package.version}' found")

    try:
        spec = importlib.util.spec_from_file_location("plugin", os.path.join(package.path, '__init__.py'))
        plugin = importlib.util.module_from_spec(spec)
        plugin.args = plugin_config
        spec.loader.exec_module(plugin)
    except Exception as e:
        print_stack()
        log.debug(e)
        raise PluginException(f"{name}: failed to load plugin")

class PluginException(Exception):
    def __init__(self, message):
        self.message = message

