from army.api.log import log
from army.api.package import find_installed_package
from army.api.debugtools import print_stack
import importlib
import importlib.util
import os

def load_plugin(name, config):
    log.info(f"load plugin '{name}'")

    package = find_installed_package(name)

    if package is None:
        raise PluginException(f"{name}: plugin not found")

    try:
        spec = importlib.util.spec_from_file_location("plugin", os.path.join(package.path(), '__init__.py'))
        plugin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin)
    except Exception as e:
        print_stack()
        log.debug(e)
        log.error(f"Failed to load plugin {name}")

class PluginException(Exception):
    def __init__(self, message):
        self.message = message
