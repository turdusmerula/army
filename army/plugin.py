import toml
import os
import sys
from log import log
from debugtools import print_stack
from version import Version
from config import PluginConfig
import importlib
import importlib.util

def load_plugin(name, config, parser):
    log.info(f"load plugin '{name}'")
    
    plugin = Plugin(name)
    plugin.load(config, parser)
    return plugin


class PluginException(Exception):
    def __init__(self, message):
        self.message = message

class Plugin():
    search_path = [
        'dist',
        '~/.army/dist',
    ]
    
    def __init__(self, name):
        self.name = name
        self.loaded = False

    def search(self):
        plugin_path = None
        plugin_version = None

        if ':' in self.name:
            name = self.name.split(':')[0]
            version = self.name.split(':')[1]
        else:
            name = self.name
            version = None

        found = False
        for path in Plugin.search_path:
            modules = self.find_module(name, path)
            log.debug(modules)
            for module in modules:
                module_name, module_version = module.split('@')

                if plugin_version is None:
                    if Version(version).dev==True and Version(module_version).dev==True:
                        found = True
                        plugin_path = os.path.join(path, module)
                        plugin_version = module_version
            
            if found:
                break

#                if version and Version()
        
        return plugin_path
    
    def find_module(self, name, dist_path):
        modules = []
        
        try:
            log.debug(f"search in '{dist_path}'")
            folders = os.listdir(os.path.expanduser(dist_path))
            for entry in folders:
                if os.path.isdir(os.path.join(dist_path, entry)) and entry.startswith(f"{name}@") :
                    modules.append(entry)
        except Exception as e:
            pass
        
        return modules
    
    def load(self, config, parser):
        plugin_path = self.search()
        if plugin_path is None:
            raise PluginException(f"plugin '{self.name}' not installed")
        log.debug(f"load plugin '{plugin_path}'")
        
        try:
            # load plugin configuration
            config = PluginConfig(None, os.path.join(plugin_path, 'army.toml'))
            config.load()
            
            entrypoint = config.entrypoint()

#             sys.path.append(os.path.dirname(os.path.join(plugin_path, entrypoint)))
            
            spec = importlib.util.spec_from_file_location("plugin", os.path.join(plugin_path, entrypoint))
            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)
            plugin.init_parser(parser, config)

        except Exception as e:
            print_stack()
            log.error(f"{e}")
            raise PluginException(f"Load failed for plugin '{self.name}'")
        
        self.loaded = True
