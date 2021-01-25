from army.api.debugtools import print_stack
from army.api.log import log, get_log_level
from army.api.prefix import prefix_path
import copy
import collections
import dpath.util
import importlib.util
import json
import os
import sys
import toml
#import oyaml as yaml
import yaml

class DictFileException(Exception):
    def __init__(self, message):
        self.message = message

def dict_file_extensions():
    return {
        "py": _load_python_dict_file, 
        "yaml": _load_yaml_dict_file, 
#         "toml": _load_toml_dict_file, 
#         "json": _load_json_dict_file
    }

def find_dict_files(path):
    path = os.path.expanduser(prefix_path(path))
    
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
def load_dict_file(path, name, exist_ok=False):
    config = None
    
    if path is None:
        path = prefix_path(os.path.dirname(name))
        if path=="":
            path = os.getcwd()
        name = os.path.basename(name)
    else:
        path = prefix_path(path)

    path = os.path.expanduser(path)
    if os.path.exists(path)==False:
        if exist_ok==True:
            return {}
        else:
            raise DictFileException(f"{path}: path not found")
    
    file = os.path.join(path, name)
    if os.path.exists(file):
        # check if file matches one of known extensions
        for ext, loader in dict_file_extensions().items():
            if name.endswith(f".{ext}"):
                config = loader(file)
                log.debug(f"content: {config}")
                return config
        
        raise DictFileException(f"{file}: unkwnown file type")
        
    # search for a file 
    config = None
    for ext, loader in dict_file_extensions().items():
        file = os.path.join(path, f"{name}.{ext}")
        if os.path.exists(file):
            if config is None:
                config = loader(file)
            else:
                log.warning(f"{file}: {name} already loaded, skipped")
            
    if config is None and exist_ok==False:
        raise DictFileException(f"{path}: no file corresponding to {name} found")
    
    if config is not None:
        log.debug(f"content: {config}")
    
    return config

def _load_python_dict_file(file):
    res = None
    # try to load python file
    with open(file) as f:
        try:
            log.info(f"load file '{file}'")
            pkg = os.path.basename(os.path.dirname(file))
            spec = importlib.util.spec_from_file_location(pkg, file)
            config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config)
            res = config.content
        except Exception as e:
            print_stack()
            log.debug(f"{e}")
            raise DictFileException(f"{file}: {e}")
    return res

def _load_yaml_dict_file(file):
    res = None
    # try to load yaml file
    with open(file) as f:
        try:
            log.info(f"load file '{file}'")
            res = yaml.load(f, Loader=yaml.FullLoader)
            if res is None:
                res = {}
        except Exception as e:
            print_stack()
            log.debug(f"{e}")
            raise DictFileException(f"{file}: {e}")
    return res

def _load_toml_dict_file(file):
    res = None
    # try to load toml file
    try:
        log.info(f"load file '{file}'")
        res = toml.load(file)
    except Exception as e:
        print_stack()
        log.debug(f"{e}")
        raise DictFileException(f"{file}: {e}")
    return res

def _load_json_dict_file(file):
    res = None
    # try to load json file
    with open(file) as f:
        try:
            log.info(f"load file '{file}'")    
            res = json.load(f)
        except Exception as e:
            print_stack()
            log.debug(f"{e}")
            raise DictFileException(f"{file}: {e}")
    return res

# TODO https://stackoverflow.com/questions/528281/how-can-i-include-a-yaml-file-inside-another
# class Loader(yaml.SafeLoader):
# 
#     def __init__(self, stream):
# 
#         self._root = os.path.split(stream.name)[0]
# 
#         super(Loader, self).__init__(stream)
# 
#     def include(self, node):
# 
#         filename = os.path.join(self._root, self.construct_scalar(node))
# 
#         with open(filename, 'r') as f:
#             return yaml.load(f, Loader)
# 
# Loader.add_constructor('!include', Loader.include)


class Dict(object):
    reserved = ["_data", "_parent"]
    
    def __init__(self, data={}, parent=None):
        self._data = data
        self._parent = parent
    
    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, item):
        return self.get(item)

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
    
    def _resolve_substs(self, path, stack):
#         value = dpath.util.get(self._data, path)
        if path.startswith('/')==False:
            path = f"/{path}"
        
        value = self.get(path, raw=True, default="")
#         print(f"{'  '*len(stack)}**", path, value)

        # put path in stack to detect variable recursion
        # when a recursion is found then we look for the path in parent dict
        stack.append(path)
            
        chuncks = self._cut_subst(value)
        res = ""
        for t, v in chuncks:
            if t==0:
                res += v
            else:
                if v.startswith('/')==False:
                    v = f"/{v}"

                if v in stack and self._parent is not None:
#                     content = self._parent.get(v, raw=True, default="")
#                     print(f"{'  '*len(stack)}==", f"{content}--{v}--{stack}")
                    res += self._parent._resolve_substs(v, stack=[])
                else:
#                     content = self.get(v, raw=True, default="")
#                     print(f"{'  '*len(stack)}++", f"{content}--{v}--{stack}")
                    res += self._resolve_substs(v, stack=stack)
#         print(f"{'  '*len(stack)}**", f"{res}")
        return res

    def get(self, path, raw=False, **kwargs):
        value = None
        try:
            if raw==True:
                value = dpath.util.get(self._data, path)
            else:
                dpath.util.get(self._data, path)    # here only to check that path exists
                value = self._resolve_substs(path, stack=[])
        except KeyError as e:
            if self._parent is None:
                if 'default' in kwargs:
                    return kwargs['default']
                raise e
            elif self._parent is not None:
                value = self._parent.get(path=path, raw=raw, **kwargs)

        return value

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
            
            try:
                return to_value(dpath.util.get(din, path))
            except KeyError as e:
                return ""
            
        def expand_value(din, value):
            chuncks = self._cut_subst(value)
            res = ""
            for t, v in chuncks:
                if t==0:
                    res += v
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
                        if key not in dout:
                            dout[key] = {}
                        copy(din[key], dout[key])
                    elif isinstance(din[key], list):
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

        for profile in reversed(parents):
            print("---", profile)
            copy(profile._data, res)
            print("+++", res)
        return res
    