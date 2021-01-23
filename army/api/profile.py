from army.api.log import log
from army.api.debugtools import print_stack
from army.api.dict_file import load_dict_file, find_dict_files


def load_profile_list():
    profiles = []
    
    profiles += load_global_profile_list()
    profiles += load_user_profile_list()
    profiles += load_project_profile_list()
    
    return profiles

# load profiles from /etc/army/profile
def load_global_profile_list():
    # load main repositories
    profiles = find_dict_files('/etc/army/profile')
    return profiles

# load profiles from ~/.army/profile
def load_user_profile_list():
    # load main repositories
    profiles = find_dict_files('~/.army/profile')
    return profiles

# load profiles from current project
def load_project_profile_list():
    # load main repositories
    profiles = []
    # TODO
    return profiles


def load_profile(profiles, name, parent=None):
    config = {}
    try:
        config = load_dict_file(path, name)
    except Exception as e:
        print_stack()
        log.debug(e)
        raise ConfigException(f"{path}/{name}: {format(e)}")
    
    try:
        res = ArmyConfigRepository(value=config, parent=parent)
    except Exception as e:
        print_stack()
        log.debug(e)
        raise ConfigException(f"{path}/{name}: {format(e)}")
        
    return res


class Profile(object):
    def __init__(self, name=None, path=None):
        self._name = name
        self._path = path
        self._data = None
        
    @property
    def name(self):
        return self._name
    
    @property
    def path(self):
        return self._path
    
    @property
    def data(self):
        return self._data

    def load(self):
        if self._data is not None:
            return
        pass