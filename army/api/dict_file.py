from army.api.debugtools import print_stack
from army.api.log import log, get_log_level
from army.api.schema import validate
import copy
import dpath.util
import importlib.util
import os
import sys
#import oyaml as yaml
import yaml
from pickle import FALSE

class DictException(Exception):
    def __init__(self, message):
        self.message = message

def dict_file_extensions():
    return {
#         "py": _load_python_dict_file, 
        "yaml": _load_yaml_dict_file, 
#         "toml": _load_toml_dict_file, 
#         "json": _load_json_dict_file
    }

def find_dict_files(path):
    path = os.path.expanduser(path)
    
    files = []
    if os.path.exists(path) and os.path.isdir(path):
        for f in os.listdir(path):
            for ext, loader in dict_file_extensions().items():
                if os.path.isfile(os.path.join(path, f)) and f.endswith(f".{ext}"):
                    name = f.replace(f".{ext}", "")
                    if name not in files:
                        files.append(name)
                        
    return files

# load a configuration file containing a dict
def load_dict_file(path, name=None, exist_ok=False, parent=None, env=None):
    res = None
    
    if path is None:
        path = os.path.dirname(name)
        if path=="":
            path = os.getcwd()
        name = os.path.basename(name)
    else:
        path = path

    path = os.path.expanduser(path)
    if os.path.exists(path)==False:
        if exist_ok==True:
            return Dict(data={}, parent=parent, env=env)
        else:
            raise DictException(f"{path}: path not found")
    
    if name is not None:
        file = os.path.join(str(path), f"{name}.yaml")
    else:
        file = path
        name = os.path.basename(path).replace(".yaml", "")
        path = os.path.dirname(path)

    if os.path.exists(file)==False and exist_ok==False:
        raise DictException(f"{path}: {name}.yaml not found")

    if os.path.exists(file)==True:
        data = _load_yaml_dict_file(file)
        if data is None and exist_ok==False:
            raise DictException(f"{path}: {name}.yaml not found")
        res = Dict(data=data, parent=parent, env=env)
#         res = Dict(data=data)
        
    if res is not None:
        log.debug(f"content: {res}")
    
    return res

def load_dict(data, parent=None, env=None):
    res = None
    # try to load yaml file
    try:
        content = yaml.safe_load(data)
        if content is None:
            content = {}
        res = Dict(data=content, parent=parent, env=env)
    except Exception as e:
        print_stack()
        log.debug(f"{e}")
        raise DictException(f"{e}")
    return res

def _load_yaml_dict_file(file):
    res = None
    # try to load yaml file
    with open(file) as f:
        try:
            log.info(f"load file '{file}'")
            res = yaml.load(f, Loader=Loader)
            if res is None:
                res = {}
        except Exception as e:
            print_stack()
            log.debug(f"{e}")
            raise DictException(f"{file}: {e}")
    return res

def save_dict_file(path, name, content):
    res = None
    file = os.path.join(str(path), f"{name}.yaml")
    # try to load yaml file
    with open(file, "w") as f:
        try:
            log.info(f"save file '{file}'")
            res = content.dump(f)
        except Exception as e:
            print_stack()
            log.debug(f"{e}")
            raise DictException(f"{file}: {e}")
    return res

# TODO https://stackoverflow.com/questions/528281/how-can-i-include-a-yaml-file-inside-another
class Loader(yaml.FullLoader):
    def __init__(self, stream):
#         self._root = os.path.split(stream.name)[0]
        super(Loader, self).__init__(stream)

#     def profile(self, node):
#         from army.api.profile import load_profile
#         chunks = self.construct_scalar(node).split('\n')
#         print("---", chunks)
# #         return load_profile(self.construct_scalar(node)).data.to_dict(), ""
#         return {'a': 1}
#     
# Loader.add_constructor('!profile', Loader.profile)

class Dict(object):
    def __init__(self, data=None, parent=None, env=None):
        if parent is not None and isinstance(parent, Dict)==False:
            raise DictException(f"{type(parent)}: parent type mismatch")
        
        self._raw_data = data
        self._parent = parent
        self._env = env
        
    def __iter__(self):
        data = self.to_dict()
        return iter(data)

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self._raw_data[key] = value

    def __len__(self):
        return len(self.to_dict())
        
    def get(self, path, raw=False, **kwargs):
        value = None
        try:
            if raw==True:
                value = dpath.util.get(self._raw_data, path)
            else:
                data = self.to_dict()
                value = dpath.util.get(data, path)
        except KeyError as e:
            if self._parent is None:
                if 'default' in kwargs:
                    return kwargs['default']
                raise e
            elif self._parent is not None:
                value = self._parent.get(path=path, raw=raw, **kwargs)
        except Exception as e:
            print(f"{e}")
        return value
 
    def _cut_subst(self, value):
        res = []
        while value!="":
            start = value.find("{{")
            end = -1
            if start>-1:
                end = value.find("}}", start)
            if start>-1 and end>-1:
                s0 = value[0:start]
                s1 = value[start+2:end].strip()
                value = value[end+2:]
                res.append([0, s0])
                res.append([1, s1])
            else:
                res.append([0, value])
                value = ""
        return res

    def delete(self, item):
        if item in self._raw_data:
            del self._raw_data[item]

    def to_dict(self):
        res = {}
        
        def get_value(din, path):
            def to_value(din):
                res= ""
                if din is None:
                    res = ""
                elif isinstance(din, dict):
                    for key in din:
                        value = to_value(din[key])
                        if value!="":
                            if res=="":
                                res = value
                            else:
                                res += f" {value}"
                elif isinstance(din, list):
                    for item in din:
                        value = to_value(item)
                        if value!="":
                            if res=="":
                                res = value
                            else:
                                res += f" {value}"
                else:
                    value = str(din)
                    if value!="":
                        if res=="":
                            res = value
                        else:
                            res += f" {value}"
                return res
            
            has_value = False
            try:
                return to_value(dpath.util.get(self._env, path))
                has_value = True
            except KeyError as e:
                pass
            
            if has_value==False:
                try:
                    return to_value(dpath.util.get(din, path))
                    has_value = True
                except KeyError as e:
                    pass
            
            if has_value==False:
                log.warn(f"{path}: substitution not found")
                return ""

        def expand_value(din, value):
            chuncks = self._cut_subst(value)
            res = ""
            for t, v in chuncks:
                if t==0:
                    # chunk type is simple text
                    res += v
                else:
                    # chunk type is a substitution
                    content = v.strip()
                    if content.startswith("package:"):
                        content = content.replace("package:", "").strip()
                        from army.api.package import find_installed_package, parse_package_name
                        chunks = parse_package_name(content)
                        path = find_installed_package(name=chunks['name'], version_range=chunks['version'], exist_ok=False)
                        res += path
                    elif content.startswith("env:"):
                        content = content.replace("env:", "")
                        res += os.getenv(content)
                    elif content.startswith("py:"):
                        content = content.replace("py:", "")
                        res += exec(content)
                        # TODO: get stdout 
                    elif ':' in content:
                        kind, content = v.split(':')
                        kind = kind.strip()
                        raise DictException(f"unknown substitution kind '{kind}'")
                    else:
                        value = get_value(din, v)
                        res += expand_value(din, value)
            return res
        
        def copy(din, dout):
            def copy_value(din):
                if isinstance(din, str):
                    nonlocal res
                    return expand_value(res, din)
                else:
                    return din

            if isinstance(din, dict):
                for key in din:
                    if isinstance(din[key], dict):
                        if key not in dout or isinstance(dout[key], dict)==False:
                            dout[key] = {}
                        copy(din[key], dout[key])
                    elif isinstance(din[key], list):
                        if key not in dout or isinstance(dout[key], list)==False:
                            dout[key] = []
                        copy(din[key], dout[key])
                    else:
                        dout[key] = copy_value(din[key])
            elif isinstance(din, list):
                for item in din:
                    if isinstance(item, dict):
                        value = {}
                        dout.append(value)
                        copy(item, value)
                    elif isinstance(item, list):
                        value = []
                        dout.append(value)
                        copy(item, value)
                    else:
                        value = copy_value(item)
                        if value!="":
                            dout.append(value)
        
        parents = []
        parent = self
        while parent is not None:
            parents.append(parent)
            parent = parent._parent

        for parent in reversed(parents):
            copy(parent._raw_data, res)

        return res
    
    def dump(self, file):
        return yaml.dump(self._raw_data, file)

    @property
    def raw_data(self):
        return self._raw_data
    
    @property
    def parent(self):
        return self._parent
    @parent.setter
    def parent(self, value):
        self._parent = value
        
    def __repr__(self):
        return str(self.to_dict())
