import toml
import os
import sys
from log import log
from debugtools import print_stack

# load army configuration files, each file supesedes the previous
# Global configuration: /etc/army/army.toml
# User configuration: ~/.army/army.tom
def load_configuration():
    files = [
        '/etc/army/army.toml',
        '~/.army/army.toml',
    ]
    config = None
    for file in files:
        config = Config(config, file)
        config.load()
        
    return config


class ConfigException(Exception):
    def __init__(self, message):
        self.message = message

class Config():
    def __init__(self, parent, file):
        self.parent = parent
        self.config = {}
        self.file = file
    
    def command_target(self):
        if 'command_target' in self.config:
            return self.config['command_target']
        if self.parent:
            return self.parent.command_target()
        return None

    def verbose(self):
        if 'verbose' in self.config:
            return self.config['verbose']
        if self.parent:
            return self.parent.verbose()
        return False
    
    def load(self):
        file = os.path.expanduser(self.file)
        if os.path.exists(file):
            try:
                self.config = toml.load(file)
                log.info(f"Loaded config '{self.file}'")
            except Exception as e:
                raise ConfigException(f"{format(e)}")

    def check_config(self):
        pass

    def write(self, path):
        with open(path, "w") as file:
            toml.dump(self.config, file)
        
def load_project(config):
#     path = os.path.abspath(os.getcwd())
#     user_path = os.path.expanduser('~')
#     if path.startswith(user_path):
#         path = path.replace(user_path, '~', 1)
#     file = os.path.join(path, "army.toml")
    
    file = 'army.toml'
    if os.path.exists(os.path.expanduser(file))==False:
        raise ConfigException("Not a project: 'army.toml' not found")
    
    config = ProjectConfig(config, file)
    config.load()
    
    return config

class ProjectConfig(Config):
    
    project_types = ['firmware', 'library', 'plugin']
    
    def __init__(self, parent, file):
        super(ProjectConfig, self).__init__(parent, file)
        
        self._project_path = os.getcwd()
        self._output_path = os.path.join(self._project_path, "output")

    def project_path(self):
        return self._project_path
    
    def check_config(self):
        super(ProjectConfig, self).check_config()
        #TODO

    def output_path(self):
        return 'output'
    
    def project_section(self):
        if 'project' in self.config:
            return self.config['project']
        else:
            raise ConfigException(f"project not defined")

    def packaging_section(self):
        if 'packaging' in self.config:
            return self.config['packaging']
        return None

    def project_name(self):
        project_section = self.project_section()

        if 'name' in project_section:
            return project_section['name']
        else:
            raise ConfigException(f"project.name not defined")

    def project_version(self):
        project_section = self.project_section()

        if 'version' in project_section:
            # TODO parse version to check validity
            # version should be x.y.z-rev, rev can be a string
            return project_section['version']
        else:
            raise ConfigException(f"project.version not defined")

    def includes(self):
        packaging_section = self.packaging_section()
        if packaging_section and 'include' in packaging_section:
            return packaging_section['include']
        return []
    
    def dependencies(self):
        res = []
        project = self.config['project']
        if 'dependencies' in project:
            for dependency in project['dependencies']:
                res.append(dependency)
        if 'target' in self.config:
            for t in self.config['target']:
                target = self.config['target'][t]
                if 'dependencies' in target:
                    for dependency in target['dependencies']:
                        res.append(dependency)
        return res
    
    
    def dev_dependencies(self):
        res = []
        project = self.config['project']
        if 'dev-dependencies' in project:
            for dependency in project['dev-dependencies']:
                res.append(dependency)
        if 'target' in self.config:
            for t in self.config['target']:
                target = self.config['target'][t]
                if 'dev-dependencies' in target:
                    for dependency in target['dev-dependencies']:
                        res.append(dependency)
        return res

    def plugins(self):
        res = []
        project = self.config['project']
        if 'plugin' in self.config:
            for plugin in self.config['plugin']:
                if 'version' in self.config['plugin'][plugin]:
                    plugin = f"{plugin}-plugin:{self.config['plugin'][plugin]['version']}"
                res.append(plugin)
        return res

    def targets(self):
        res = []
        if 'target' in self.config:
            return self.config['target']
        return res
    
    def default_target(self):
        project = self.config['project']
        if 'default-target' in project:
            return project['default-target']
        return None
        

def load_module(config, module_path):
    file = 'army.toml'
    if os.path.exists(os.path.join(module_path, file))==False:
        raise ConfigException("Not a module: 'army.toml' not found")
    
    config = ComponentConfig(config, os.path.join(module_path, file))
    config.load()
    
    return config

class ComponentConfig(ProjectConfig):

    def __init__(self, parent, file):
        super(ComponentConfig, self).__init__(parent, file)

    def includes(self):
        if 'packaging' not in self.config:
            return []
        packaging = self.config['packaging']
        if 'include' in packaging:
            return packaging['include']
        return []
    
    def excludes(self):
        if 'packaging' not in self.config:
            return []
        packaging = self.config['packaging']
        if 'exclude' in packaging:
            return packaging['exclude']
        return []

    def arch(self):
        res = []
        project = self.config['project']
        if 'arch' in project:
            return self.config['project']['arch']
        return res
    
    def cmake(self):
        res = None
        project = self.config['project']
        if 'cmake' in project:
            return self.config['project']['cmake']
        return res
        
class PluginConfig(Config):

    def __init__(self, parent, file):
        super(PluginConfig, self).__init__(parent, file)

    def entrypoint(self):
        if 'entrypoint' in self.config['project']:
            return self.config['project']['entrypoint']
        return 'plugin/plugin.py'
    