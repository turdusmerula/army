import toml
import os
import sys
from army.api.log import log
from army.api.debugtools import print_stack

# load army configuration files, each file supersedes the previous
# Global configuration: /etc/army/army.toml
# User configuration: ~/.army/army.tom
# @param prefix mainly used for unit tests purpose
def load_configuration(prefix=""):
    files = [
        '/etc/army/army.toml',
        '~/.army/army.toml',
    ]
    config = None
    for file in files:
        config = Config(config, os.path.join(prefix, file))
        config.load()
        
    return config



class ConfigException(Exception):
    def __init__(self, message):
        self.message = message

# Configuration base class
class Config():
    ITEM_TYPE=0
    ITEM_DEFAULT_VALUE=1

    def __init__(self, value=None, parent=None, fields=None):
        self._parent = parent
        self._value = value
        
        # configuration fields
        # key: field name
        # value: [ <item class>, default value ]
        self._fields = fields
        
        self.check() ;
        
    def parent(self):
        return self._parent 

    # get item value stored inside the item
    def value(self):
        return self._value

    # check value content
    def check(self):
        if isinstance(self._value, dict):
            err = None
            # check all fields
            for value in self._value:
                try:
                    self.get(value)
                except ConfigException as e:
                    err = f"{err}\n{e}: unknown value"
            
            if err:
                raise ConfigException(err)

    # load the configuration
    # should be overriden if special thing needs to be done such as loading a file
    def load(self):
        pass

    # get subitem value
    def get(self, item):
        if self._fields is None or item not in self._fields:
            raise ConfigException(f"'{item}': value not found")
    
        value = None
        if isinstance(self.value(), dict) and item in self.value():
            # instantiate configuration item from loaded value
            value = self.value()[item]
        elif self.parent():
            # parent exists, ask item value to it
            return self.parent().get(item)
        else:
            # item not found in herarchy, return default value
            value = self._fields[item][self.ITEM_DEFAULT_VALUE]
    
        return self._fields[item][self.ITEM_TYPE](value=value)

    def expand(self):
        res = None
        if self._fields:
            res = {}
        else:
            return self._value
        
        if isinstance(self._value, dict):
            for value in self._value:
                res[value] = self._value[value]
        
        for field in self._fields:
            if field not in res:
                res[field] = self.get(field).expand()

        return res
                
        
    def __str__(self):
        return f"{self.value()}"

class ConfigString(Config):
    def __init__(self, value=None, parent=None):
        super(ConfigString, self).__init__(value, parent)
    
    def check(self):
        if not isinstance(self.value(), str):
            raise ConfigException(f"'{self.value()}': invalid string")

class ConfigInt(Config):
    def __init__(self, value=None, parent=None):
        super(ConfigInt, self).__init__(value, parent)

    def check(self):
        if not isinstance(self.value(), int):
            raise ConfigException(f"'{self.value()}': invalid integer")
    
    def __int__(self):
        return self._value
    
# class ArmyConfig(Config):
#     def __init__(self, parent, file):
#         super(ArmyConfig, self).__init__(parent)
#         
#         self._fields = {
#             { 'verbose', [ str, False ]}
#         }
# 
# class ArmyConfigFile(Config):
#     def __init__(self, parent, file):
#         super(ArmyConfigFile, self).__init__(parent, file)
#     
#     def command_target(self):
#         if 'command_target' in self.config:
#             return self.config['command_target']
#         if self.parent:
#             return self.parent.command_target()
#         return None
# 
#     def verbose(self):
#         if 'verbose' in self.config:
#             return self.config['verbose']
#         if self.parent:
#             return self.parent.verbose()
#         return False
#     
#     def load(self):
#         file = os.path.expanduser(self.file)
#         if os.path.exists(file):
#             try:
#                 self.config = toml.load(file)
#                 log.info(f"Loaded config '{self.file}'")
#             except Exception as e:
#                 raise ConfigException(f"{format(e)}")
# 
#     def check_config(self):
#         # TODO
#         pass
# 
#     def write(self, path):
#         with open(path, "w") as file:
#             toml.dump(self.config, file)
