import toml
import os
import sys
from army.api.log import log
from army.api.debugtools import print_stack
from army.api.config import ArmyConfigFile, Config, ConfigString, ConfigVersion
from army.api.config import ConfigList, ConfigStringList, ConfigDict

# load project army file 
# @param parent parent configuration
# @param prefix mainly used for unit tests purpose
# @return the loaded project configuration or None if project was not loaded
def load_project(parent=None, prefix=""):
    
    # load main config file
    config = ArmyProjectFile(parent=parent, file=os.path.join(prefix, 'army.toml'))

    return config

class ConfigPackaging(Config):
    def __init__(self, value=None, parent=None):
        super(ConfigPackaging, self).__init__(
            value=value,
            parent=parent,
            fields={
                'include': [ ConfigStringList, [] ],
                'exclude': [ ConfigStringList, [] ]
            }
        )

class ConfigProject(Config):
    def __init__(self, value=None, parent=None):
        super(ConfigProject, self).__init__(
            value=value,
            parent=parent,
            fields={
                'name': [ ConfigString ],
                'description': [ ConfigString ],
                'version': [ ConfigVersion ],
                'dependencies': [ ConfigRepositoryList, [] ],
                'dev-dependencies': [ ConfigRepositoryList, [] ]
            }
        )

class ConfigPlugin(Config):
    def __init__(self, value=None, parent=None):
        super(ConfigPlugin, self).__init__(
            value=value,
            parent=parent,
            fields={}
        )

class ConfigPluginDict(ConfigDict):
    def __init__(self, parent=None, value=None):
        super(ConfigPluginDict, self).__init__(
            parent=parent,
            value=value,
            field=[ ConfigPlugin, {} ]
        )


class ArmyProjectFile(ArmyConfigFile):
    def __init__(self, file, parent=None):
        super(ArmyProjectFile, self).__init__(
            file=file,
            parent=parent,
            fields={
                'project': [ ConfigProject ],
                'packaging': [ ConfigPackaging, {} ],
                'plugin': [ ConfigPluginDict, {} ]
            }
        )
    

class ConfigRepositoryList(ConfigList):
    
    def __init__(self, parent=None, value=None):
        super(ConfigRepositoryList, self).__init__(
            parent=parent,
            value=value,
            field=[ ConfigString, "" ]
        )
