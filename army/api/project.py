from army.api.log import log
from army.api.debugtools import print_stack
from army.api.package import Package
from army.api.schema import SchemaException
import toml
import toml.decoder
import os
import sys

# from army.api.config import ArmyConfigFile, Config, ConfigString, ConfigVersion
# from army.api.config import ConfigList, ConfigStringList, ConfigDict

# load project army file 
# @param parent parent configuration
# @param prefix mainly used for unit tests purpose
# @return the loaded project configuration or None if project was not loaded
def load_project(path='army.toml'):
    
    # TODO find a way to add line to error message
    file = os.path.expanduser(path)
    if os.path.exists(file)==False:
        raise ProjectException(f"{file}: file not found")

    content = {}
    try:
        log.info(f"Load project '{file}'")
        content = toml.load(file)
        log.debug(f"content: {content}")
    except toml.decoder.TomlDecodeError as e:
        print_stack()
        log.debug(e)        
        raise e
    except Exception as e:
        print_stack()
        log.debug(e)
        raise ProjectException(f"{format(e)}")
    
    project = Project(data=content)
    project.check()
        

    return project

class ProjectException(Exception):
    def __init__(self, message):
        self.message = message


class Project(Package):
    def __init__(self, data):
        super(Project, self).__init__(data, schema={})
