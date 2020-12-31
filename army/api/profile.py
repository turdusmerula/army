from army.api.log import log
from army.api.debugtools import print_stack
from army import prefix

profiles = {}

# load profiles from ./profile and ~/.army/profile
def _load_static_profile_list():
    pass

# load profiles from project dependencies
def _load_project_profile_list():
    pass

def load_profile_list():
    global profiles
    
    _load_static_profile_list()
    _load_project_profile_list()
    
    return profiles


class Profile(object):
    def __init__(self):
        self._path = None
        self._name = None
        self._description = None
        self._data = {}
        
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
