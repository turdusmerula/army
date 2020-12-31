from army.api.log import log, get_log_level
from army.api.debugtools import print_stack
import importlib.util
import toml
import json
import yaml
import os
import sys

class DictFileException(Exception):
    def __init__(self, message):
        self.message = message

# load a configuration file containing a dict
def load_dict_file(path, name, exist_ok=False):
    res = None
    
    if os.path.exists(os.path.expanduser(path))==False:
        if exist_ok==True:
            return {}
        else:
            raise DictFileException(f"{path}: path not found")
    
    # try to load python file
    file = os.path.join(path, f"{name}.py")
    if res is None and os.path.exists(file)==True:
        with open(file) as f:
            try:
                pkg = os.path.basename(os.path.dirname(file))
                spec = importlib.util.spec_from_file_location(pkg, file)
                config = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config)
                res = config.content
            except Exception as e:
                print_stack()
                log.debug(f"{e}")
                raise DictFileException(f"{file}: {e}")
        log.info(f"loaded file {file}")
    
    # try to load yaml file
    file = os.path.join(path, f"{name}.yaml")
    if res is None and os.path.exists(file)==True:
        with open(file) as f:
            try:
                res = yaml.load(f, Loader=yaml.FullLoader)
            except Exception as e:
                print_stack()
                log.debug(f"{e}")
                raise DictFileException(f"{file}: {e}")
        log.info(f"loaded file {file}")
    if res is not None and os.path.exists(file)==True:
        log.warning(f"{file}: {name} already loaded, skipped")
        
    # try to load toml file
    file = os.path.join(path, f"{name}.toml")
    if res is None and os.path.exists(file)==True:
        try:
            res = toml.load(file)
        except Exception as e:
            print_stack()
            log.debug(f"{e}")
            raise DictFileException(f"{file}: {e}")
        log.info(f"loaded file {file}")
    if res is not None and os.path.exists(file)==True:
        log.warning(f"{file}: {name} already loaded, skipped")
    
    # try to load json file
    file = os.path.join(path, f"{name}.json")
    if res is None and os.path.exists(file)==True:
        with open(file) as f:
            try:
                res = json.load(f)
            except Exception as e:
                print_stack()
                log.debug(f"{e}")
                raise DictFileException(f"{file}: {e}")
        log.info(f"loaded file {file}")
    if res is not None and os.path.exists(file)==True:
        log.warning(f"{file}: {name} already loaded, skipped")
    
    if res is None and exist_ok==False:
        raise DictFileException(f"{path}: no file corresponding to {name} found")
    
    if res is not None:
        log.debug(f"content: {res}")
    
    return res
