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
    i=0
    # load main config file
    config = ArmyConfigFile(parent=parent, file=os.path.join(prefix, 'etc/army/army.toml'))
    config.load()
    
    # load main repositories
    path = os.path.join(prefix, 'etc/army/repo.d')
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)) and f.endswith(".toml"):
#            config = ConfigRepository(parent=config, value=)
            config = ConfigRepositoryFile(parent=config, file=os.path.join(path, f))
            config.load()

    # load user config file
    config = ArmyConfigFile(parent=config, file=os.path.join(prefix, '~/.army/army.toml'))
    config.load()
    
    # load user repositories
    path = os.path.join(prefix, '~/.army/repo.d')
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)) and f.endswith(".toml"):
#            config = ConfigRepository(parent=config, value=)
            config = ConfigRepositoryFile(parent=config, file=os.path.join(path, f))
            config.load()


    return config



class ConfigException(Exception):
    def __init__(self, message):
        self.message = message


# Configuration base class
class BaseConfig(object):

    def __init__(self, value=None, parent=None):
        super(BaseConfig, self).__init__()
        
        self._parent = parent
        self._value = value
        
    def parent(self):
        return self._parent 

    # get item value stored inside the item
    def value(self):
        return self._value


class Config(BaseConfig):
    ITEM_TYPE=0
    ITEM_DEFAULT_VALUE=1

    def __init__(self, value=None, parent=None, fields=None):
        super(Config, self).__init__(value=value, parent=parent)
        
        # configuration fields
        # key: field name
        # value: [ <item class>, default value ]
        self._fields = fields
        
        self.check() ;
        
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

    def get_fields(self):
        if self._fields:
            return self._fields
        return {}

    def get_field(self, item):
        if self._fields and item in self._fields:
            return self._fields[item]
        if self._parent:
            return self._parent.get_field(item)
        return None
    
    # @description get subitem value
    # @param item name of the item to look for
    # @param default when the item is not found, if True  return its default value, when False return None
    def get(self, item, default=True):
        # check that field exists somewhere in the configuration tree
        field = self.get_field(item)
        
        if field is None:
            raise ConfigException(f"'{item}': value not found")
    
        value = None
        if isinstance(self.value(), dict) and item in self.value():
            # item exists in the current configuration
            # instantiate configuration item from loaded value
            value = self.value()[item]
        elif self.parent() and self.parent().get_field(item) is None:
            # item does not exists either in the parent
            if default==True:
                # set default value
                value = field[self.ITEM_DEFAULT_VALUE]
            else:
                # no value
                value = None
        elif self.parent():
            # parent exists and has the item
            value = self.parent().get(item).value()

        if value:
            # we have a value
            return field[self.ITEM_TYPE](value=value)
        elif default==True:
            # item not found in herarchy, return default value
            return field[self.ITEM_TYPE](value=field[self.ITEM_DEFAULT_VALUE])
        return None

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
        
    def expand(self, default=True):
        res = None
        if self._fields:
            res = {}
        else:
            return self._value
        
        if self.parent():
            res = self.parent().expand(default)
        
        for item in self.get_fields():
#            field = self.get_field(item)
            value = self.get(item, default)
            if value:
                res[item] = value.expand()

        return res

    def __str__(self):
        return f"{self.value()}"


class ConfigString(Config):
    def __init__(self, value=None, parent=None):
        super(ConfigString, self).__init__(value=value, parent=parent)
    
    def check(self):
        if not isinstance(self.value(), str):
            raise ConfigException(f"'{self.value()}': invalid string")


class ConfigInt(Config):
    def __init__(self, value=None, parent=None):
        super(ConfigInt, self).__init__(value=value, parent=parent)

    def check(self):
        if not isinstance(self.value(), int):
            raise ConfigException(f"'{self.value()}': invalid integer")
    
    def __int__(self):
        return self._value


class _ConfigDictIterator(object):
    def __init__(self, values):
        self._list = values
        
        if values.parent():
            self._items = { **values.parent().value(), **values.value()}
        self._iter = iter(self._items)
     
    def __next__(self):
        return next(self._iter)
#         return self._list.get_field()[ConfigDict.ITEM_TYPE](value=val)
 

class ConfigDict(BaseConfig):
    ITEM_TYPE=0
    ITEM_DEFAULT_VALUE=1

    def __init__(self, value=None, parent=None, field=None):
        super(ConfigDict, self).__init__(value=value, parent=parent)

        # fields will contain only the type of dict items
        self._field = field

        self.check() ;
 
    def check(self):
        if self._parent and not isinstance(self.parent(), ConfigDict):
            raise ConfigException(f"'{self.parent()}': invalid parent type")
        
        if not isinstance(self.value(), dict):
            raise ConfigException(f"'{self.value()}': invalid value dict")
         
    def get_field(self):
        return self._field
    
    def append(self, name, item):
        # check that field exists somewhere in the configuration tree
        field = self.get_field()
        
        if isinstance(item, type(field))==False:
            raise ConfigException(f"{item}: invilad type")
        
        self.value()[name] = item.value()
        
    def expand(self):
        res = None
        if self._field:
            res = {}
        else:
            return self._value
        
        for item in self:
            res[item] = self[item].expand()
        return res
    
    def __len__(self):
        if self.parent():
            return len({ **self.parent().value(), **self.value() })
        return len(self.value())
    
    def __getitem__(self, name):
        # check that field exists somewhere in the configuration tree
        field = self.get_field()
        
        if field is None:
            raise ConfigException(f"None type found")

        value = None
        if self.value() and name in self.value():
            # item exists in the current configuration
            # instantiate configuration item from loaded value
            return field[self.ITEM_TYPE](value=self.value()[name])
        elif self.parent():
            return self.parent()[name]
        else:
            raise ConfigException(f"{name}: does not exists")
            
        return None

    def __str__(self):
        return f"{self.value()}"

    def __iter__(self):
        return _ConfigDictIterator(self)


class _ConfigListIterator(object):
    def __init__(self, list):
        self._list = list
#         self._field = field
#         self._list = values
        self._index = 0
#         self._iter = iter(values)
    
    def __next__(self):
        if self._index<len(self._list):
            res = self._list[self._index]
            self._index += 1
            return res
        raise StopIteration()
    
class ConfigList(BaseConfig):
    ITEM_TYPE=0
    ITEM_DEFAULT_VALUE=1

    def __init__(self, value=None, parent=None, field=None):
        super(ConfigList, self).__init__(value=value, parent=parent)

        # fields will contain only the type of dict items
        self._field = field

        self.check() ;

    def check(self):
        if self._parent and not isinstance(self.parent(), ConfigList):
            raise ConfigException(f"'{self.parent()}': invalid parent type")
        
        if not isinstance(self.value(), list):
            raise ConfigException(f"'{self.value()}': invalid value list")

    def get_field(self):
        return self._field
    
    def append(self, item):
        # check that field exists somewhere in the configuration tree
        field = self.get_field()
        
        if isinstance(item, type(field))==False:
            raise ConfigException(f"{item}: invilad type")
        
        self.value().append(item.value())
        
    def expand(self, default=True):
        res = None
        if self._field:
            res = []
        else:
            return self._value
        
        for item in self:
            res.append(item.expand())
        return res
    
    def __len__(self):
        res = len(self.value())
        if self.parent():
            res += len(self.parent())
        return res 
    
    def __getitem__(self, index):
        # check that field exists somewhere in the configuration tree
        field = self.get_field()
        
        if field is None:
            raise ConfigException(f"None type found")

        if index<0 or index>=len(self):
            raise ConfigException(f"{index}: out of bounds")
            
        value = None
        if index<len(self.value()):
            # item exists in the current configuration
            # instantiate configuration item from loaded value
            return field[self.ITEM_TYPE](value=self.value()[index])
        elif self.parent():
            pindex = index-len(self.value())
            return self.parent()[pindex]

        return None

    def __str__(self):
        return f"{self.value()}"

    def __iter__(self):
        return _ConfigListIterator(self)


# TODO: create type ConfigEnum as base class
class ConfigLogLevel(ConfigString):
    def __init__(self, value=None, parent=None):
        super(ConfigLogLevel, self).__init__(value=value, parent=parent)

    def check(self):
        super(ConfigLogLevel, self).check() 
        if self._value not in {"debug", "info", "warning", "error", "critical"}:
            raise ConfigException(f"'{self.value()}': invalid value")


class ArmyConfig(Config):
    def __init__(self, parent=None, fields=None):
        super(ArmyConfig, self).__init__(
            parent=parent,
            fields={
                'verbose': [ ConfigLogLevel, "error" ]
            }
        )


class ArmyConfigFile(ArmyConfig):
    def __init__(self, file, parent=None):
        super(ArmyConfigFile, self).__init__(
            parent=parent,
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
            field=[ ConfigRepository, {} ]
        )

class ConfigRepositoryFile(Config):
    def __init__(self, file, parent=None, value=None):
        super(ConfigRepositoryFile, self).__init__(
            parent=parent,
            value=value,
            fields={
                "repo": [ ConfigRepositoryList, [] ]
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
                config_toml = toml.load(file)
                log.debug(config)
            except Exception as e:
                print_stack()
                raise ConfigException(f"{format(e)}")
            
#             for item in config_toml:
#                 if item=="repo":
#                     # merge instead of replacing
#                     for r in config_toml[item]:
#                         repo = ConfigRepository(value={
#                             'name:': 
#                             })
#                         self.get(item).append(config_toml[item])
#                 else:
#                     self.set(item, config_toml[item])

