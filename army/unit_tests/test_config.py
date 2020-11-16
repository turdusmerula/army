from army.api.config import Config, ConfigException,  ConfigString, ConfigInt
from army.api.log import log
import os

# get current file path to find ressource files
path = os.path.dirname(__file__)
log.setLevel('DEBUG') # default log mode warning


def raised(func, *args,**kwargs):
    res = False
    try:
        func(*args,**kwargs)
    except Exception as e:
        res = type(e)
#         print(e)
    return res



s = ConfigString(value="value")
assert str(s)=="value"

# check raise with improper values
assert raised(ConfigString)==ConfigException
assert raised(ConfigString, 0)==ConfigException
assert raised(ConfigString, True)==ConfigException
assert raised(ConfigInt)==ConfigException
assert raised(ConfigInt, "aaaaa")==ConfigException

class TestConfig(Config):
    def __init__(self, value=None, parent=None):
        super(TestConfig, self).__init__(value, parent,
            fields={
                'value1': [ ConfigString, "v1" ],
                'value2': [ ConfigInt, 5 ],
                'value3': [ ConfigInt, 10 ]
            })
    

# no config set, check we are finding the default values
c1 = TestConfig() ;
assert str(c1.get('value1'))=='v1'
assert str(c1.value1)=='v1'
assert int(c1.value2)==5
assert int(c1.value3)==10
print("c1:", c1.expand())

# values are set, check that we find them 
c2 = TestConfig(value={
    "value1": "v2",
    "value2": 1
    })
assert str(c2.value1)=='v2'
assert int(c2.value2)== 1
assert int(c2.value3)== 10
print("c2:", c2.expand())

# child configuration overrides 
c3 = TestConfig(value={
    "value2": 2
    }, parent=c2)
print(type(c3.value1))
assert str(c3.value1)=='v2'
assert int(c3.get('value2'))==2
assert int(c3.get('value3'))==10
print("c3:", c3.expand())

class ConfigStringEnum(ConfigString):
    def __init__(self, value=None, parent=None):
        super(ConfigStringEnum, self).__init__(value, parent)

    def check(self):
        super(ConfigStringEnum, self).check() 
        if self.value not in {"a", "b", "c"}:
            raise ConfigException(f"'{self.value}': invalid value")

assert raised(ConfigStringEnum)==ConfigException
assert raised(ConfigStringEnum, "d")==ConfigException
c4 = ConfigStringEnum("a")
assert str(c4)=='a'
print("c4:", c4.expand())


class TestConfig2(Config):
    def __init__(self, value=None, parent=None):
        super(TestConfig2, self).__init__(value, parent,
            fields={
                'config1': [ TestConfig, {} ],
                'config2': [ TestConfig, { "value1": "test" } ],
                'value1': [ ConfigStringEnum, "b" ]
            })
    

c5 = TestConfig2()
print("c5:", c5.expand())
assert str(c5.get("config1").get("value1"))=="v1"
assert int(c5.get("config1").get("value2"))==5
assert str(c5.get("config2").get("value1"))=="test"
assert int(c5.get("config2").get("value2"))==5
assert str(c5.get("value1"))=="b"

c6 = TestConfig2(value={
    "config1": {"value1": 'test1'},
    "value1": "c"
    })
print("c6:", c6.expand())
assert str(c6.get("config1").get("value1"))=="test1"
assert int(c6.get("config1").get("value2"))==5
assert str(c6.get("config2").get("value1"))=="test"
assert int(c6.get("config2").get("value2"))==5
assert str(c6.get("value1"))=="c"

c7 = TestConfig2(value={
    "config1": {"value2": 10},
    }, parent=c6)
print("c7:", c7.expand())
assert str(c7.get("config1").get("value1"))=="v1"
assert int(c7.get("config1").get("value2"))==10
assert str(c7.get("config2").get("value1"))=="test"
assert int(c7.get("config2").get("value2"))==5
assert str(c7.get("value1"))=="c"

class TestConfig3(Config):
    def __init__(self, value=None, parent=None):
        super(TestConfig3, self).__init__(value, parent,
            fields={
                'value2': [ ConfigString, "test" ]
            })
c8 = TestConfig3(value={
    "value2": "test2",
    }, parent=c7)
print("c8:", c8.expand())
assert str(c8.get("config1").get("value1"))=="v1"
assert int(c8.get("config1").get("value2"))==10
assert str(c8.get("config2").get("value1"))=="test"
assert int(c8.get("config2").get("value2"))==5
assert str(c8.get("value1"))=="c"
assert str(c8.get("value2"))=="test2"

c8.set("value1", "a")
assert str(c8.get("value1"))=="a"

assert raised(c8.set, "value1", "d")==ConfigException
assert str(c8.get("value1"))=="a"


##############################
# test army config files loading
from army.api.config import ArmyConfigFile, load_configuration, ConfigRepository, ConfigRepositoryDict, ConfigRepositoryFile
from army.api.config import ConfigList

# check simple file load
c9 = ArmyConfigFile(file=os.path.join(path, "test_data/etc/army/army.toml"))
print("c9:", c9.expand())
assert str(c9.get("verbose"))=="debug"

class ConfigListItem(Config):
    def __init__(self, parent=None, value=None):
        super(ConfigListItem, self).__init__(
            parent=parent,
            value=value,
            fields={
                'name': [ ConfigString, "" ],
                'type': [ ConfigString, "" ],
                'uri': [ ConfigString, "" ],
            }
        )

c10a = ConfigList(
    value=[
            {'name': 'repo_test1', 'type': 'git-local', 'uri': '~/git/repo_test1'}, 
            {'name': 'repo_test2', 'type': 'git-local', 'uri': '~/git/repo_test2'}
        ],
    field=[ConfigListItem, {}]
    )
c10b = ConfigList(
    value=[
            {'name': 'repo_test3', 'type': 'git-local', 'uri': '~/git/repo_test3'}, 
            {'name': 'repo_test4', 'type': 'git-local', 'uri': '~/git/repo_test4'}
        ],
    field=[ConfigListItem, {}],
    parent=c10a
    )
assert len(c10a)==2
assert len(c10b)==4
assert str(c10a[0].get('name'))=='repo_test1'
assert str(c10b[0].get('name'))=='repo_test3'
assert str(c10b[2].get('name'))=='repo_test1'
i=0
for item in c10b:
    print(f"c10b[{i}]:", item) #.get('name'))
    i += 1 
print("c10b:", c10b.expand())


c11a = ConfigRepositoryDict(
    value={
            'repo_test1': {'type': 'git-local', 'uri': '~/git/repo_test1'}, 
            'repo_test2': {'type': 'git-local', 'uri': '~/git/repo_test2'},
            'repo_test3': {'type': 'git-local', 'uri': '~/git/repo_test3'}
        },
    )
c11b = ConfigRepositoryDict(
    value={
            'repo_test3': {'type': 'git', 'uri': 'http://github.com/repo_test3'}, 
            'repo_test4': {'type': 'git-local', 'uri': '~/git/repo_test4'}
        },
    parent=c11a
    )
assert len(c11a)==3
assert len(c11b)==4
assert str(c11a['repo_test1'].get('uri'))=='~/git/repo_test1'
assert str(c11a['repo_test3'].get('type'))=='git-local'
assert str(c11b['repo_test3'].get('type'))=='git'

for item in c11b:
    print(f"c11b['{item}']:", c11b[item]) #.get('name'))
print("c11b:", c11b.expand())
# 
c12 = ConfigRepositoryFile(file=os.path.join(path, "test_data/etc/army/repo.d/repo_test1-2.toml"))
assert len(c12.repo)==2
assert str(c12.get("repo")["repo_test1"].get('type'))=='git-local'
# 
print(f"load test files from {path}")
config=load_configuration(prefix=os.path.join(path, "test_data"))
print("c12:", config.expand())
assert len(config.repo)==6
assert str(config.repo['main'].type)=='git-local'
assert str(config.repo['repo_test2'].type)=='git'
# check iterator
repos={}
for repo in config.repo:
    repos[repo] = repo
print(repos)
assert len(repos)==6
