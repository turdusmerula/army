from army.api.log import log
from army.api.version import Version
from army.api.config import load_configuration, ConfigException
from army.api.project import load_project, ConfigProject, ArmyProjectFile
import os

def raised(func, *args,**kwargs):
    res = False
    try:
        func(*args,**kwargs)
    except Exception as e:
        res = type(e)
#         print(e)
    return res

# get current file path to find ressource files
path = os.path.dirname(__file__)
log.setLevel('DEBUG') # default log mode warning

print(f"load test files from {path}")
config=load_configuration(prefix=os.path.join(path, "test_data"))
print("config", config.expand())

assert raised(ConfigProject)==ConfigException

p1 = ConfigProject(value={
        'name': "project",
        'description': "test",
        'version': "1.0.0"
    })
print( p1.expand() )

p2 = ArmyProjectFile(file=os.path.join(path, "test_data/~/git/project1/army.toml"), parent=config)
assert str(p2.project.name)=="project1"
