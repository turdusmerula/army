from army.api.config import load_configuration
from army.api.log import log
import os
# from schema import Schema, And, Use, Optional

# get current file path to find ressource files
path = os.path.dirname(__file__)
prefix = os.path.join(path, 'test_config')

log.setLevel('DEBUG')

def raised(func, *args,**kwargs):
    res = False
    try:
        func(*args,**kwargs)
    except Exception as e:
        res = type(e)
        print(e)
    return res

# check no error when loading
assert raised(load_configuration, None, prefix)==False
config = load_configuration(None, prefix)

# show loaded configuration
parent = config
while parent is not None:
    print(parent, parent.value)
    parent = parent.parent

# check repositories
print(len(config.repo))
print(config.repo.value)
for item in config.repo:
    print(item)
assert len(config.repo)==6

# check attributes
assert config.verbose=="debug"

assert raised(lambda: config.toto)==AttributeError
