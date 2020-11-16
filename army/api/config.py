import toml
import os
import sys
from army.api.log import log
from army.api.debugtools import print_stack
from army.api.version import Version
from schema import Schema, And, Use, Optional

repo_schema = {
    "type": str,
    "uri": str
}

repo_dict_schema = {
    str: repo_schema
}

config_file_schema = {
    Optional('verbose'): And(lambda s: s in ["debug", "info", "warning", "error", "critical"], error="verbose: invalid log level"),
    Optional('repo'): repo_dict_schema
}

config_repository_file_schema = {
    Optional('repo'): {
        str: repo_schema
    }
}

# load army configuration files, each file supersedes the previous
# Global configuration: /etc/army/army.toml
# User configuration: ~/.army/army.tom
# @param parent parent configuration
# @param prefix mainly used for unit tests purpose
def load_configuration(parent=None, prefix=None):
    # load main config file
    config = ArmyConfig(parent=parent)
    path = os.path.join(prefix or "/", 'etc/army/army.toml')
    if os.path.exists(path):
        config = load_configuration_file(path=path, parent=parent)
    
    # load main repositories
    path = os.path.join(prefix or "/", 'etc/army/repo.d')
    if os.path.exists(path) and os.path.isdir(path):
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)) and f.endswith(".toml"):
                config = load_configuration_repository_file(path=os.path.join(path, f), parent=config)

    # load user config file
    path = os.path.join(prefix or "", '~/.army/army.toml')
    if os.path.exists(os.path.expanduser(path)):
        config = load_configuration_file(path=path, parent=config)
     
    # load user repositories
    path = os.path.join(prefix or "", '~/.army/repo.d')
    if os.path.exists(os.path.expanduser(path)) and os.path.isdir(os.path.expanduser(path)):
        for f in os.listdir(os.path.expanduser(path)):
            if os.path.isfile(os.path.join(os.path.expanduser(path), f)) and f.endswith(".toml"):
                config = load_configuration_repository_file(path=os.path.join(path, f), parent=config)

    return config


def load_configuration_file(path, parent=None):
    # TODO find a way to add line to error message
    file = os.path.expanduser(path)
    if os.path.exists(file)==False:
        raise ConfigException(f"{file}: file not found")

    config = {}
    try:
        log.info(f"load config '{path}'")
        config = toml.load(file)
        log.debug(f"content: {config}")
    except Exception as e:
        print_stack()
        log.debug(e)
        raise ConfigException(f"{format(e)}")
    
    try:
        res = ArmyConfig(parent=parent, value=config)
    except Exception as e:
        print_stack()
        log.debug(e)
        raise ConfigException(f"{format(e)}")
        
    return res

def load_configuration_repository_file(path, parent=None):
    # TODO find a way to add line to error message
    file = os.path.expanduser(path)
    if os.path.exists(file)==False:
        raise ConfigException(f"{file}: file not found")

    config = {}
    try:
        log.info(f"Load config '{path}'")
        config = toml.load(file)
        log.debug(f"content: {config}")
    except Exception as e:
        print_stack()
        log.debug(e)
        raise ConfigException(f"{format(e)}")
    
    try:
        res = ArmyConfigRepository(value=config, parent=parent)
    except Exception as e:
        print_stack()
        log.debug(e)
        raise ConfigException(f"{format(e)}")
        
    return res



class ConfigException(Exception):
    def __init__(self, message):
        self.message = message

class Config(object):
    def __init__(self, value=None, parent=None, schema={}):
        self._value = value
        self._parent = parent
        self._schema = Schema(schema)

        if value is not None:
            log.debug(f"validate: {self.value} with {self.schema}")
            self.schema.validate(self.value)
        
    @property
    def value(self):
        return self._value
    
    @property
    def parent(self):
        return self._parent

    @property
    def schema(self):
        return self._schema

    def __getattr__(self, name):
        if self.parent is not None:
            return getattr(self.parent, name)
        raise AttributeError(f"'{type(self)}' object has no attribute '{name}'")
        
    def get(self, name, default=None):
        if self.value is None or name not in self.value:
            if self.parent is not None:
                return self.parent.get(name, default)
        elif self.value is not None and name in self.value:
            return self.value[name]
        return default

    def _recursive_get_dict(self, name, values):
        if self.value is not None and name in self.value:
            for item in self.value[name]:
                if item not in values:
                    values[item] = self.value[name][item]
        if self.parent is not None:
            return self.parent._recursive_get_dict(name, values)
        return values

    def recursive_get_dict(self, name, default={}):
        values = {}
        if self.value is not None and name in self.value:
            for item in self.value[name]:
                if item not in values:
                    values[item] = self.value[name][item]
        if self.parent is not None:
            values = self.parent._recursive_get_dict(name, values)
        
        for item in default:
            if item not in values:
                values[item] = default[item]
                
        return values
        
class _ConfigDictIterator(object):
    def __init__(self, values):
        self.values = values
        self._iter = iter(self.values)
      
    def __next__(self):
        return next(self._iter)
#         return self._list.get_field()[ConfigDict.ITEM_TYPE](value=val)

class ConfigDict(Config):
    def __init__(self, value=None, item_type=None, schema={}):
        super(ConfigDict, self).__init__(value=value, schema=schema)
        self.item_type = item_type

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return _ConfigDictIterator(self.value)

    def __getitem__(self, name):
        return self.item_type(value=self.value[name])


class ArmyConfig(Config):
    def __init__(self, value=None, parent=None):
        super(ArmyConfig, self).__init__(
            value=value,
            parent=parent,
            schema=config_file_schema
        )

    @property
    def verbose(self):
        return self.get('verbose', 'critical')

    @property
    def repo(self):
        return ConfigDict(self.recursive_get_dict('repo'), ConfigRepository, schema=repo_dict_schema)

class ArmyConfigRepository(Config):
    def __init__(self, value=None, parent=None):
        super(ArmyConfigRepository, self).__init__(
            value=value,
            parent=parent,
            schema=config_repository_file_schema
        )

    @property
    def repo(self):
        return ConfigDict(self.recursive_get_dict('repo'), ConfigRepository, schema=repo_dict_schema)



class ConfigRepository(Config):
    def __init__(self, value=None, parent=None):
        super(ConfigRepository, self).__init__(
            value=value,
            parent=parent,
            schema=repo_schema
        )

    @property
    def type(self):
        return self.get('type')
        
    @property
    def uri(self):
        return self.get('uri')
