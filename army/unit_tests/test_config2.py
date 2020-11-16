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

#assert raised(load_configuration, None, prefix)==False

config = load_configuration(None, prefix)

parent = config
while parent is not None:
    print(parent, parent.value)
    parent = parent.parent

for item in config.repo:
    print(item)

print(config.repo.value)
print(config.verbose)

assert raised(lambda: config.toto)==AttributeError

# class Config(object):
#     def __init__(self, value=None, parent=None, schema={}):
#         self._value = value
#         self._parent = parent
#         self._schema = Schema(schema)
# 
#     @property
#     def value(self):
#         return self._value
#     
#     @property
#     def parent(self):
#         return self._parent
# 
#     @property
#     def schema(self):
#         return self._schema
# 
#     def get(self, name, default=None):
#         if self.value is None or name not in self.value:
#             if self.parent is not None:
#                 return self.parent.get(name, default)
#         return default
#     
# 
# class ArmyConfigRepository(Config):
#     def __init__(self, parent=None, value=None):
#         super(ArmyConfigRepository, self).__init__(
#             parent=parent,
#             value=value,
#             fields={
#                 'repo': [ ConfigRepositoryDict, {}, self._allocate_repo ]
#             }
#         )
