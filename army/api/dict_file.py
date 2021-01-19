from army.api.log import log, get_log_level
from army.api.debugtools import print_stack
from army.api.prefix import prefix_path
import importlib.util
import toml
import json
import yaml
import os
import sys

class DictFileException(Exception):
    def __init__(self, message):
        self.message = message

def dict_file_extensions():
    return {
        "py": _load_python_dict_file, 
        "yaml": _load_yaml_dict_file, 
        "toml": _load_toml_dict_file, 
        "json": _load_json_dict_file
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
        path = prefix_path(os.path.expanduser(os.path.dirname(name)))
        if path=="":
            path = os.getcwd()
        print(path)
        name = os.path.basename(name)
    else:
        path = prefix_path(os.path.expanduser(path))

    if os.path.exists(os.path.expanduser(path))==False:
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

