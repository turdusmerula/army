from army.api.log import log
from army.api.debugtools import print_stack
from army.api.dict_file import load_dict_file, find_dict_files, Dict
import copy

# cache for available profiles
profiles = None

class ProfileException(Exception):
    def __init__(self, message):
        self.message = message

def load_profile_list():
    global profiles
    
    if profiles is not None:
        return profiles
    
    profiles = []
    
#     profiles += load_global_profile_list()
    profiles += load_user_profile_list()
#     profiles += load_project_profile_list()
    
    return profiles

# load profiles from /etc/army/profile
def load_global_profile_list():
    # load main repositories
    profiles = find_dict_files('/etc/army/profile')
    return profiles

# load profiles from ~/.army/profile
def load_user_profile_list():
    profiles = []
    # load main repositories
    dicts = find_dict_files('~/.army/profile')
    for name in dicts:
        profile = Profile(name=name, path='~/.army/profile')
        profiles.append(profile)
    return profiles

# load profiles from current project
def load_project_profile_list():
    # load main repositories
    profiles = []
    # TODO
    return profiles


def load_profile(name, parent=None):
    res = None
    
    profiles = load_profile_list()
    
    # search profile in profiles list
    for profile in profiles:
        if profile.name==name:
            res = copy.copy(profile)
            res._parent = parent
            res.load()
            return res
    
    if res is None:
        raise ProfileException(f"{name}: profile not found")
        
    return res


class Profile(object):
    def __init__(self, name=None, path=None, parent=None):
        self._name = name
        self._path = path
        self._parent = parent
        self._description = ""
        self._data = None
        
    @property
    def name(self):
        return self._name
    
    @property
    def path(self):
        return self._path
    
    @property
    def description(self):
        return self._description

    @property
    def data(self):
        return self._data

    def load(self):
        if self._data is not None:
            return
        
        parent = None
        if self._parent is not None:
            parent = self._parent._data
        
        self._data = Dict(load_dict_file(self.path, self.name), parent=parent)
