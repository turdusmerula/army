from army.api.debugtools import print_stack
from army.api.dict_file import load_dict_file, find_dict_files
from army.api.log import log
from army.api.path import prefix_path
from army.api.schema import validate, Optional, Choice
from army.api.version import Version
import toml
import os
import sys

# load army global file in /etc/army
# @param parent parent configuration
def load_global_configuration(parent=None):
    # load main config file
    config = load_configuration_file(path=prefix_path('/etc/army'), name='army', parent=parent)
#      
#     # load user repositories
#     path = os.path.join(prefix or "", '~/.army/repo.d')
#     if os.path.exists(os.path.expanduser(path)) and os.path.isdir(os.path.expanduser(path)):
#         for f in os.listdir(os.path.expanduser(path)):
#             if os.path.isfile(os.path.join(os.path.expanduser(path), f)) and f.endswith(".toml"):
#                 config = load_configuration_repository_file(path=os.path.join(path, f), parent=config)

    return config

def load_global_configuration_repositories(parent=None):
    config = parent
    # load main repositories
    path = prefix_path('/etc/army/repo.d')
    files = find_dict_files(path)
    for file in files:
        config = load_configuration_repository_file(path=path, name=file, parent=config)

    return config

# load army user file in ~/.army
# @param parent parent configuration
def load_user_configuration(parent=None):
    # load user config file
    config = load_configuration_file(path=prefix_path('~/.army'), name='army', parent=parent)
    return config

def load_user_configuration_repositories(parent=None):
    config = parent
    # load main repositories
    path = prefix_path('~/.army/repo.d')
    files = find_dict_files(path)
    for file in files:
        config = load_configuration_repository_file(path=path, name=file, parent=config)
    return config

def load_configuration_file(path, name, parent=None):
    try:
        res = Config(path=path, name=name, parent=parent)
        res.load()
    except Exception as e:
        print_stack()
        log.debug(e)
        raise ConfigException(f"{path}/{name}: {format(e)}")
        
    return res

def load_configuration_repository_file(path, name, parent=None):
    try:
        res = ConfigRepository(path=path, name=name, parent=parent)
        res.load()
    except Exception as e:
        print_stack()
        log.debug(e)
        raise ConfigException(f"{path}/{name}: {format(e)}")
        
    return res



class ConfigException(Exception):
    def __init__(self, message):
        self.message = message

class Config(object):
    _schema = {
        Optional('verbose'): Choice("debug", "info", "warning", "error", "critical", error="invalid log level"),
        Optional('repositories'): {
            "type": str,
            "uri": str
        }
    }
    
    def __init__(self, path, name, parent=None):
        if parent is not None and isinstance(parent, Config)==False:
            raise ConfigException(f"{type(parent)}: parent type mismatch")
                
        self._path = path
        self._name = name
        self._parent = parent
        self._data = None
        
        self._schema = Config._schema

    def load(self, validate=True):
        if self._data is not None:
            return
        
        parent = None
        if self._parent is not None:
            parent = self._parent._data
            
        self._data = load_dict_file(self._path, self._name, parent=parent, exist_ok=True)
        if validate:
            self.validate()
        
    def validate(self):
        validate(self._data, self._schema)

    class Repository(object):
        def __init__(self, type, uri):
            self._type = type
            self._uri = uri
            
        @property
        def type(self):
            return self._type
             
        @property
        def uri(self):
            return self._uri

    @property
    def repositories(self):
        repos = self._data.get("repositories", default={})
        res = {}
        for repo in repos:
            res[repo] = Config.Repository(type=repos[repo]['type'], uri=repos[repo]['uri'])
        return res
    
class ConfigRepository(Config):
    _schema = {
        Optional('repositories'): {
            "type": str,
            "uri": str
        }
    }
    
    def __init__(self, path, name, parent=None):
        super(ConfigRepository, self).__init__(path, name, parent)

        self._schema = ConfigRepository._schema

#     def __init__(self, value=None, parent=None, schema={}):
#         self._value = value
#         self._parent = parent
#         self._schema = schema
#         
#     @property
#     def value(self):
#         return self._value
#     
#     @property
#     def parent(self):
#         return self._parent
# 
#     @property
#     def schema(self):
#         return self._schema
# 
#     def validate(self):
#         validate(self._value.to_dict(), self._schema)
#         
#     def __getattr__(self, name):
#         if self.parent is not None:
#             return getattr(self.parent, name)
#         raise AttributeError(f"'{type(self)}' object has no attribute '{name}'")
#         
#     def get(self, name, default=None):
#         if self.value is None or name not in self.value:
#             if self.parent is not None:
#                 return self.parent.get(name, default)
#         elif self.value is not None and name in self.value:
#             return self.value[name]
#         return default
# 
#     def _recursive_get_dict(self, name, values):
#         if self.value is not None and name in self.value:
#             for item in self.value[name]:
#                 if item not in values:
#                     values[item] = self.value[name][item]
#         if self.parent is not None:
#             return self.parent._recursive_get_dict(name, values)
#         return values
# 
#     def recursive_get_dict(self, name, default={}):
#         values = {}
#         if self.value is not None and name in self.value:
#             for item in self.value[name]:
#                 if item not in values:
#                     values[item] = self.value[name][item]
#         if self.parent is not None:
#             values = self.parent._recursive_get_dict(name, values)
#         
#         for item in default:
#             if item not in values:
#                 values[item] = default[item]
#                 
#         return values
#         
# class _ConfigDictIterator(object):
#     def __init__(self, values):
#         self.values = values
#         self._iter = iter(self.values)
#       
#     def __next__(self):
#         return next(self._iter)
# #         return self._list.get_field()[ConfigDict.ITEM_TYPE](value=val)
# 
# class ConfigDict(Config):
#     def __init__(self, value=None, item_type=None, schema={}):
#         super(ConfigDict, self).__init__(value=value, schema=schema)
#         self.item_type = item_type
# 
#     def __len__(self):
#         return len(self.value)
# 
#     def __iter__(self):
#         return _ConfigDictIterator(self.value)
# 
#     def __getitem__(self, name):
#         return self.item_type(value=self.value[name])
# 
# 
# class ArmyConfig(Config):
#     def __init__(self, value=None, parent=None, path=None):
#         super(ArmyConfig, self).__init__(
#             value=value,
#             parent=parent,
#             schema=config_file_schema
#         )
#         self._path = path
#         
#     @property
#     def path(self):
#         return self._path
#         
#     @property
#     def verbose(self):
#         return self.get('verbose', 'critical')
# 
#     @property
#     def repositories(self):
#         return ConfigDict(self.recursive_get_dict('repositories'), ConfigRepository, schema=repo_dict_schema)
# 
# class ArmyConfigRepository(Config):
#     def __init__(self, value=None, parent=None):
#         super(ArmyConfigRepository, self).__init__(
#             value=value,
#             parent=parent,
#             schema=config_repository_file_schema
#         )
# 
#     @property
#     def repositories(self):
#         return ConfigDict(self._value.get("repositories"), ConfigRepository, schema=repo_dict_schema)
# #         return ConfigDict(self.recursive_get_dict('repositories'), ConfigRepository, schema=repo_dict_schema)
# 
# 
# 
