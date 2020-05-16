import toml
import os
import sys
from army.api.log import log
from army.api.debugtools import print_stack

# load army configuration files, each file supersedes the previous
# Global configuration: /etc/army/army.toml
# User configuration: ~/.army/army.tom
# @param parent parent configuration
# @param prefix mainly used for unit tests purpose
def load_configuration(parent=None, prefix="/"):
    
    # load main config file
    config = ArmyConfigFile(parent=parent, file=os.path.join(prefix, 'etc/army/army.toml'))
    config.load()
    
    # load main repositories
    path = os.path.join(prefix, 'etc/army/repo.d')
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)) and f.endswith(".toml"):
#            config = ConfigRepository(parent=config, value=)
            config = ArmyConfigFile(parent=config, file=os.path.join(path, f))
            config.load()
    
    # load user config file
    config = ArmyConfigFile(parent=config, file=os.path.join(prefix, '~/.army/army.toml'))
    config.load()
    
    # load user repositories


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

    def get_field(self, item):
        if self._fields and item in self._fields:
            return self._fields[item]
        if self._parent:
            return self._parent.get_field(item)
        return None
    
    # get subitem value
    def get(self, item):
        field = self.get_field(item)
        
        if field is None:
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
            value = field[self.ITEM_DEFAULT_VALUE]
    
        return field[self.ITEM_TYPE](value=value)

    def set(self, item, value):
        field = self.get_field(item)
        
        if field is None:
            raise ConfigException(f"'{item}': value not found")
        
        if self._value is None:
            self._value = {}
            
        if self._value and not isinstance(self._value, dict):
            # this should not happen, means there is a problem to investigate upstream
            raise ConfigException(f"'{item}': parent type mismatch")
        
        v = field[self.ITEM_TYPE](value=value)
        self._value[item] = v.value()
        
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


class _ConfigDictIterator(object):
    def __init__(self, values):
        self._list = values
        self._iter = iter(values)
    
    def __next__(self):
        res = next(self._iter)
        return res


class ConfigDict(Config):
    def __init__(self, value=None, parent=None, item=None):
        super(ConfigDict, self).__init__(value, parent)

        self._item = item

    def check(self):
        if not isinstance(self.value(), dict):
            raise ConfigException(f"'{self.value()}': invalid value list")
    
    def get(self, item):
        field = self._item
        
        if field is None:
            raise ConfigException(f"'{item}': dict type not defined")
    
        value = None
        if isinstance(self.value(), dict) and item in self.value():
            # instantiate configuration item from loaded value
            value = self.value()[item]
        elif self.parent():
            # parent exists, ask item value to it
            return self.parent().get(item)
        else:
            # item not found in herarchy, return default value
            value = field[self.ITEM_DEFAULT_VALUE]
    
        return field[self.ITEM_TYPE](value=value)
    
    def count(self):
        return len(self._value)

    def __iter__(self):
        return _ConfigDictIterator(self._value)


class ConfigLogLevel(ConfigString):
    def __init__(self, value=None, parent=None):
        super(ConfigLogLevel, self).__init__(value, parent)

    def check(self):
        super(ConfigLogLevel, self).check() 
        if self.value() not in {"debug", "info", "warning", "error", "critical"}:
            raise ConfigException(f"'{self.value()}': invalid value")


class ArmyConfig(Config):
    def __init__(self, parent=None, fields=None):
        super(ArmyConfig, self).__init__(
            parent,
            fields={
                'verbose': [ ConfigLogLevel, "error" ]
            }
        )


class ArmyConfigFile(ArmyConfig):
    def __init__(self, file, parent=None):
        super(ArmyConfigFile, self).__init__(
            parent,
            fields={
            }
        )
        self._file = file
    
    def file(self):
        return self._file 
    
    def load(self):
        # TODO find a way to add line to error message
        file = os.path.expanduser(self._file)
        if os.path.exists(file):
            config = {}
            try:
                log.info(f"Load config '{self._file}'")
                config = toml.load(file)
                log.debug(config)
            except Exception as e:
                print_stack()
                raise ConfigException(f"{format(e)}")
            
            for item in config:
                self.set(item, config[item])


class ConfigRepository(Config):
    def __init__(self, parent=None, value=None):
        super(ConfigRepository, self).__init__(
            parent=parent,
            value=value,
            fields={
                'type': [ ConfigString, "" ],
                'uri': [ ConfigString, "" ],
            }
        )
    
class ConfigRepositoryDict(ConfigDict):
    def __init__(self, parent=None, value=None):
        super(ConfigRepositoryDict, self).__init__(
            parent=parent,
            value=value,
            item=[ ConfigRepository, {} ]
        )

class ConfigRepositoryFile(Config):
    def __init__(self, file, parent=None, value=None):
        super(ConfigRepositoryFile, self).__init__(
            parent=parent,
            value=value,
            fields={
                "repo": [ ConfigRepositoryDict, {} ]
            }
        )
        self._file = file
    
    def load(self):
        # TODO find a way to add line to error message
        file = os.path.expanduser(self._file)
        if os.path.exists(file):
            config = {}
            try:
                log.info(f"Load repository config '{self._file}'")
                config = toml.load(file)
                log.debug(config)
            except Exception as e:
                print_stack()
                raise ConfigException(f"{format(e)}")
            
            for item in config:
                self.set(item, config[item])

