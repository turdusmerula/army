import toml
import os
import sys
from army.api.log import log
from army.api.debugtools import print_stack
from army.api.version import Version

# load army configuration files, each file supersedes the previous
# Global configuration: /etc/army/army.toml
# User configuration: ~/.army/army.tom
# @param parent parent configuration
# @param prefix mainly used for unit tests purpose
def load_configuration(parent=None, prefix="/"):
    # load main config file
    config = ArmyConfigFile(parent=parent, file=os.path.join(prefix, 'etc/army/army.toml'))
    
    # load main repositories
    path = os.path.join(prefix, 'etc/army/repo.d')
    if os.path.exists(path) and os.path.isdir(path):
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)) and f.endswith(".toml"):
                config = ConfigRepositoryFile(parent=config, file=os.path.join(path, f))

    # load user config file
    path = os.path.join(prefix, '~/.army/army.toml')
    if os.path.exists(path):
        config = ArmyConfigFile(parent=config, file=path)
     
    # load user repositories
    path = os.path.join(prefix, '~/.army/repo.d')
    if os.path.exists(path) and os.path.isdir(path):
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)) and f.endswith(".toml"):
                config = ConfigRepositoryFile(parent=config, file=os.path.join(path, f))

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

    def set_parent(self, parent):
        self._parent = parent
        self.check()

    # get item value stored inside the item
    def value(self):
        return self._value


class Config(BaseConfig):
    ITEM_TYPE=0          # mandatory: field type
    ITEM_DEFAULT_VALUE=1 # mandatory: define default field value
    ITEM_ALLOCATOR=2     # facultative: custom allocator for field

    def __init__(self, value=None, parent=None, fields=None):
        super(Config, self).__init__(value=value, parent=parent)
        
        # configuration fields
        # key: field name
        # value: [ <item class>, default value ]
        self._fields = fields
        
        self.load() ;
        
    # check value content
    def check(self):
        # check for mandatory fields
        for field_name in self.get_fields():
            field = self.get_field(field_name)

            if isinstance(field, list)==False:
                raise ConfigException(f"{field_name}: invalid field format")                
            if len(field)==0:
                raise ConfigException(f"{field_name}: missing field type")
            if len(field)==1 and ( self._value is None or field_name not in self._value):
                raise ConfigException(f"{field_name}: missing value")
                
        
        # check for extraneous elements
        if isinstance(self._value, dict):
            err = []
            # check all fields
            for value in self._value:
                if self.get_field(value) is None:
                    raise ConfigException(f"{value}: unexpected value")
#             for value in self._value:
#                 try:
#                     self.get(value)
#                 except ConfigException as e:
#                     err.append(f"{e}")
#                     
#             if len(err)>0:
#                 raise ConfigException(err)

    def load(self):
        self.check() 

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
            raise ConfigException(f"'{item}': unexpected value")

        if len(field)==3:
            # custom allocator given for this field
            allocator = field[self.ITEM_ALLOCATOR]
        else:
            # use default allocator
            allocator = field[self.ITEM_TYPE]
        
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
            return allocator(value=value)
        elif default==True:
            # item not found in herarchy, return default value
            return allocator(value=field[self.ITEM_DEFAULT_VALUE])
        return None

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            if self.get_field(name):
                return object.__getattribute__(self, "get")(name)
            else:
                raise AttributeError(name)
    
    def set(self, item, value):
        field = self.get_field(item)

        if field is None:
            raise ConfigException(f"'{item}': unexpected value")
        
        if self._value is None:
            self._value = {}
            
        if self._value and not isinstance(self._value, dict):
            # this should not happen, means there is a problem to investigate upstream
            raise ConfigException(f"'{item}': parent type mismatch")
        
        # create an item, should trigger an error if content is invalid
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


class ConfigVersion(Config):
    def __init__(self, value=None, parent=None):
        super(ConfigVersion, self).__init__(value=Version(value), parent=parent)

    def check(self):
        if not isinstance(self.value(), Version):
            raise ConfigException(f"'{self.value()}': invalid version")

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
        
        self._items = values.value()
        parent = values.parent()
        while parent:
            self._items = { **parent.value(), **self._items }
            parent = parent.parent()

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

        self.load() ;
 
    def check(self):
        if self._parent and not isinstance(self.parent(), ConfigDict):
            raise ConfigException(f"'{self.parent()}': invalid parent type")
        
        if not isinstance(self.value(), dict):
            raise ConfigException(f"'{self.value()}': invalid value dict")
         
    def load(self):
        self.check()
        
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
        
        if self.parent():
            res = self.parent().expand()

        for item in self:
            res[item] = self[item].expand()

        return res
    
    def __len__(self):
        list = self.value()
        parent = self.parent()
        while parent:
            list = { **parent.value(), **list }
            parent = parent.parent()
        return len(list)
    
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

        self.load() ;

    def check(self):
        if self._parent and not isinstance(self.parent(), ConfigList):
            raise ConfigException(f"'{self.parent()}': invalid parent type")
        
        if not isinstance(self.value(), list):
            raise ConfigException(f"'{self.value()}': invalid value list")

    def load(self):
        self.check()
        
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
    def __init__(self, parent=None, fields={}):
        super(ArmyConfig, self).__init__(
            parent=parent,
            fields={
                **fields,
                'verbose': [ ConfigLogLevel, "error" ]
            }
        )


class ArmyConfigFile(ArmyConfig):
    def __init__(self, file, parent=None, fields={}):
        self._file = file

        super(ArmyConfigFile, self).__init__(
            parent=parent,
            fields={
                **fields,
                "repo": [ ConfigRepositoryDict, {}, self._allocate_repo ]
            }
        )
    
    def file(self):
        return self._file 
    
    def load(self):
        # TODO find a way to add line to error message
        file = os.path.expanduser(self._file)
        if os.path.exists(file)==False:
            raise ConfigException(f"{file}: file not found")

        config = {}
        try:
            log.info(f"Load config '{self._file}'")
            config = toml.load(file)
            log.debug(f"content: {config}")
        except Exception as e:
            print_stack()
            raise ConfigException(f"{format(e)}")
        
        for item in config:
            try:
#                 log.debug(f"load '{item}': {config[item]}")
                self.set(item, config[item])
            except Exception as e:
                print_stack()
                log.error(f"{self._file}: {e}")
        self.check()
        
    # define a custom allocator for the repo field, this field is not replaced by childs but needs to be merged
    # as each child just adds or superseed repository list
    def _allocate_repo(self, value):
        res = ConfigRepositoryDict(value=value)
        current = res
        
        # merge repository list with parent repo
        parent = self.parent()
        while(parent):
            try:
                if(parent.get_field('repo')):
                    new = ConfigRepositoryDict(value=parent.repo.value())
                    current.set_parent(new)
                    current = new
            except:
                pass
            parent = parent.parent()

        if parent:  
            return ConfigRepositoryDict(value=value, parent=parent.repo)
        return res

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
        self._file = file

        super(ConfigRepositoryFile, self).__init__(
            parent=parent,
            value=value,
            fields={
                "repo": [ ConfigRepositoryDict, {}, self._allocate_repo ]
            }
        )
        
    def load(self):
        # TODO find a way to add line to error message
        file = os.path.expanduser(self._file)
        if os.path.exists(file):
            config_toml = {}
            try:
                log.info(f"Load repository config '{self._file}'")
                config_toml = toml.load(file)
                log.debug(f"content: {config_toml}")
            except Exception as e:
                print_stack()
                raise ConfigException(f"{format(e)}")
            
            self._value = config_toml
            self.check()
    
    # define a custom allocator for the repo field, this field is not replaced by childs but needs to be merged
    # as each child just adds or superseed repository list
    def _allocate_repo(self, value):
        res = ConfigRepositoryDict(value=value)
        current = res
        
        # merge repository list with parent repo
        parent = self.parent()
        while(parent):
            try:
                if(parent.get_field('repo')):
                    new = ConfigRepositoryDict(value=parent.repo.value())
                    current.set_parent(new)
                    current = new
            except:
                pass
            parent = parent.parent()

        if parent:  
            return ConfigRepositoryDict(value=value, parent=parent.repo)
        return res
