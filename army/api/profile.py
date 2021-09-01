from army.api.log import log
from army.api.debugtools import print_stack
from army.api.dict_file import load_dict_file, find_dict_files
from army.api.path import prefix_path
from army.api.schema import validate, Optional, Use
from army.api.version import Version, VersionRange
import copy
import json
import os

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
    
    profiles += load_global_profile_list()
    profiles += load_user_profile_list()
    profiles += load_project_profile_list()
    
    return profiles

# load profiles from /etc/army/profile
def load_global_profile_list():
    profiles = []
    # load main repositories
    dicts = find_dict_files(prefix_path('/etc/army/profile'))
    for name in dicts:
        chunks = parse_profile_name(name)
        try:
            profile = Profile(name=chunks['name'], version=chunks['version'], path=prefix_path('/etc/army/profile'))
            profiles.append(profile)
        except Exception as e:
            print_stack()
            log.error(f"{e}")
        
    return profiles

# load profiles from ~/.army/profile
def load_user_profile_list():
    profiles = []
    # load main repositories
    dicts = find_dict_files(prefix_path('~/.army/profile'))
    for name in dicts:
        chunks = parse_profile_name(name)
        try:
            profile = Profile(name=chunks['name'], version=chunks['version'], path=prefix_path('~/.army/profile'))
            profiles.append(profile)
        except Exception as e:
            print_stack()
            log.error(f"{e}")
        
    return profiles

# load profiles from current project
def load_project_profile_list():
    # load main repositories
    profiles = []
    dicts = find_dict_files('profile')
    for name in dicts:
        chunks = parse_profile_name(name)
        try:
            profile = Profile(name=chunks['name'], version=chunks['version'], path='profile')
            profiles.append(profile)
        except Exception as e:
            print_stack()
            log.error(f"{e}")
            
    return profiles

def load_profile(name, parent=None, validate=True):
    profiles = load_profile_list()
    
    chunks = parse_profile_name(name)
    sname = chunks['name']
    sversion = chunks['version']
    if sversion is None:
        sversion = 'latest'
    
    found = None

    # search in profiles without a version first
    if sversion=='latest':
        for profile in profiles:
            if profile.name==chunks['name'] and profile.version is None:
                found = profile
    
    if found is None:
        # search in versioned profiles
        versions = []
        for profile in profiles:
            if profile.name==chunks['name'] and profile.version is not None:
                versions.append(profile.version)
        if len(versions)>0:
            version = VersionRange(versions)[sversion]
            if version is not None:
                for profile in profiles:
                    if profile.name==chunks['name'] and Version(profile.version)==version:
                        found = profile
    if found is None:
        raise ProfileException(f"{name}: profile not found")

    res = copy.copy(found)
    res._parent = parent
    res.load(validate=validate)
    return res
    

def load_current_profile(validate=True):
    path = ".army-profile"
    
    if os.path.exists(path)==False:
        return None
    
    with open(path, "r") as f:
        profiles = json.load(f)

    profile = None
    for name in profiles:
        profile = load_profile(name, profile, validate=validate)
    
    return profile

def load_current_profile_cache():
    path = ".army-profile"
    
    if os.path.exists(path)==False:
        return []
    
    with open(path, "r") as f:
        return json.load(f)

def save_current_profile_cache(profiles):
    path = ".army-profile"
        
    with open(path, "w") as f:
        json.dump(profiles, f)


def parse_profile_name(profile_name):
    res = {
        'name': profile_name,
        'version': None
    }
    
    chunks = profile_name.split('@')
    if len(chunks)==2:
        res['name'] = chunks[0]
        res['version'] = chunks[1]

        # check chunks[1] is a valid version range
        VersionRange(['1.0.0'])[chunks[1]]
    elif len(chunks)!=1:
        raise ProfileException(f"{profile_name}: incorrect profile name")
    
    return res

class Profile(object):
    _schema = {
        Optional('profiles'): [{
            'name': str,
            'version': str 
        }],
        Optional('plugins'): [{
            'name': str,
            'version': Use(VersionRange),
            'config': {
                str: object
            },
        }],
        Optional('tools'): {
            str: object
        },
        Optional('env'): {
            str: str
        }
    }
    
    def __init__(self, name=None, version=None, path=None, parent=None):
                
        self._name = name
        self._version = version
        self._path = path
        self._parent = parent
        self._description = None
        self._data = None
        
        self._schema = Profile._schema
        
    @property
    def name(self):
        return self._name
    
    @property
    def version(self):
        return self._version

    @property
    def path(self):
        return self._path
    
    @property
    def description(self):
        return self._description

    @property
    def data(self):
        return self._data

    @property
    def parent(self):
        return self._parent

    def load(self, validate=True):
        if self._data is not None:
            return
        
        parent = None
        if self._parent is not None:
            parent = self._parent._data

        if self.version is None:
            name = f"{self.name}"
        else:
            name = f"{self.name}@{self.version}"
            
        self._data = load_dict_file(self.path, name, parent=parent)
        if validate:
            self.validate()
        
        self._description = self._data.get("/description", raw=True, default="")
        
        # load subprofiles
        for profile in self.data.get("profiles", raw=True, default={}):
            name = profile.get("name")
            version = profile.get("version")
            profile_data = load_profile(f"{name}@{version}", validate=validate)
            if self._data._parent is not None:
                profile_data._data.parent = self._data.parent
            self._data.parent = profile_data._data
        self._data.delete("profiles")
        
    def validate(self):
        validate(self._data, self._schema)

    def to_dict(self):
        return self._data.to_dict()