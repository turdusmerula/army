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
       
    def is_verbose(self):
        if 'verbose' in self.config:
            return self.config['verbose']
        if self.parent:
            return self.parent.is_verbose()
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


# Project configuration: .army/army.toml
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