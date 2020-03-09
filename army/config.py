import toml
import os
import sys

# load army configuration files, each file supesedes the previous
# Global configuration: /etc/army/army.toml
# User configuration: ~/.army/army.tom
def load_configuration():
    files = [
        '/etc/army/army.toml',
        os.path.join(os.path.expanduser('~'), '/.army/army.toml'),
    ]
    config = None
    for file in files:
        config = Config(config)
        config.load_config(file)
        
    return config


class ConfigException(Exception):
    def __init__(self, message):
        self.message = message

class Config():
    def __init__(self, parent):
        self.parent = parent
        self.config = {}

       
    def is_verbose(self):
        if 'verbose' in self.config:
            return self.config['verbose']
        if self.parent:
            return self.parent.is_verbose()
        return False
    
    def load_config(self, file):
        if os.path.exists(file):
            try:
                self.config = toml.load(file)
                print(self.config)
            except Exception as e:
                print(f"{format(e)}")
                exit(1)

    def check_config(self):
        pass


# Project configuration: .army/army.toml
def load_project_configuration(config):
    if os.path.exists("army.toml")==False:
        return None
    
    config = ProjectConfig(config)
    config.load_config(os.path.join(os.getcwd(), "army.toml"))
    
    return config

class ProjectConfig(Config):
    
    project_types = ['firmware', 'library', 'plugin']
    
    def __init__(self, parent):
        super(ProjectConfig, self).__init__(parent)
    
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